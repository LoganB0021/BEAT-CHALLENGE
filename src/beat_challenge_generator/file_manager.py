from datetime import datetime
import hashlib
import os
import tempfile
import zipfile
import random
import string
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import BEAT_DIR, OUTPUT_DIR, PACKS_DIR
from beat_challenge_generator.models import Pack

def generate_random_name(length=8):
    """Generate a random string for the zip file name."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def add_to_zip(zipf, file_path, arcname):
    """Adds a file or an entire folder to the zip archive."""
    if os.path.isdir(file_path):  # If it's a folder, add all its contents
        for root, _, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(root, file)
                file_path = os.path.relpath(full_path, BEAT_DIR)  # Preserve folder structure
                zipf.write(full_path, file_path)
                logger.info(f"📂 Added folder file: {file_path}")
    else:  # If it's a file, add it normally
        zipf.write(file_path, arcname)
        logger.info(f"📄 Added file: {arcname}")

def create_beat_pack(selected_files):
    """Creates a zip file with the selected beat components, including folders."""
    if not selected_files:
        logger.warning("⚠️ No files selected for beat pack.")
        return None

    pack_name = f"beat_{generate_random_name()}.zip"
    pack_path = os.path.join(OUTPUT_DIR, pack_name)

    try:
        with zipfile.ZipFile(pack_path, 'w') as zipf:
            for category, item in selected_files.items():
                item_path = os.path.join(BEAT_DIR, category, item)

                if os.path.exists(item_path):
                    add_to_zip(zipf, item_path, os.path.join(category, item))
                else:
                    logger.error(f"❌ Item not found: {item_path}")

        logger.info(f"🎉 Beat pack created: {pack_path}")
        return pack_path

    except Exception as e:
        logger.error(f"🚨 Error creating beat pack: {e}")
        return None
    
def create_pack(selected_sounds: dict, db: Session, pack_date=None, mode="daily"):
    """
    Create a Pack record in DB and write zip to PACKS_DIR.

    Args:
        selected_sounds (dict): {category: Sound instance}
        db (Session): SQLAlchemy session

    Returns:
        str: Path to the created zip file
    """
    os.makedirs(PACKS_DIR, exist_ok=True)

    pack_date = pack_date or datetime.today().strftime("%Y-%m-%d")
    name = f"pack_{pack_date}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    zip_filename = os.path.join(PACKS_DIR, f"pack_{timestamp}_{uuid4().hex}.zip")
    temp_path = None
    beat_root = Path(BEAT_DIR).resolve()

    try:
        validated = []
        for category, sound in selected_sounds.items():
            source = Path(sound.file_path).resolve()
            if source != beat_root and beat_root not in source.parents:
                raise ValueError(f"Selected path is outside the beats directory: {source}")
            if not source.exists():
                raise FileNotFoundError(f"Selected file/folder does not exist: {source}")
            validated.append((category, sound, source))

        fd, temp_path = tempfile.mkstemp(prefix=".pack-", suffix=".tmp", dir=PACKS_DIR)
        os.close(fd)
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for category, sound, source in validated:
                if sound.is_folder:
                    for root, _, files in os.walk(source):
                        for file in files:
                            full_path = Path(root) / file
                            relative = full_path.relative_to(source).as_posix()
                            zf.write(full_path, f"{category}/{source.name}/{relative}")
                else:
                    zf.write(source, f"{category}/{source.name}")

        os.replace(temp_path, zip_filename)
        temp_path = None

        size_bytes = os.path.getsize(zip_filename)
        digest = hashlib.sha256()
        with open(zip_filename, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        checksum = digest.hexdigest()

        pack = Pack(
            name=name,
            date=pack_date,
            seed=int(datetime.today().strftime("%Y%m%d")),
            zip_path=zip_filename,
            size_bytes=size_bytes,
            checksum=checksum,
            items=[sound.id for sound in selected_sounds.values()],
            status="generated",
            generated_by=f"file_selector:{mode}",
            updated_at=datetime.now(),
        )
        db.add(pack)
        db.commit()
        logger.info(f"✅ Pack created at {zip_filename} with DB record ID {pack.id}")
        return zip_filename
    except Exception:
        db.rollback()
        if temp_path:
            try:
                os.remove(temp_path)
            except FileNotFoundError:
                pass
        if os.path.exists(zip_filename):
            try:
                os.remove(zip_filename)
            except FileNotFoundError:
                pass
        raise
