from datetime import datetime
import hashlib
import os
import zipfile

from sqlalchemy.orm import Session
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import OUTPUT_DIR
from beat_challenge_generator.models import Pack
    
def create_pack(selected_sounds: dict, db: Session):
    """
    Create a Pack record in DB and write zip to OUTPUT_DIR.

    Args:
        selected_sounds (dict): {category: Sound instance}
        db (Session): SQLAlchemy session

    Returns:
        str: Path to the created zip file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create deterministic name based on date
    today_str = datetime.today().strftime("%Y-%m-%d")
    name = f"pack_{today_str}"

    # Use timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(OUTPUT_DIR, f"pack_{timestamp}.zip")

    # Create the zip file
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
        for category, sound in selected_sounds.items():
            if not os.path.exists(sound.file_path):
                logger.warning(f"⚠️ File/folder does not exist: {sound.file_path}")
                continue

            if sound.is_folder:
                # Add folder contents recursively
                for root, _, files in os.walk(sound.file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Preserve category folder structure inside zip
                        arcname = os.path.join(category, os.path.relpath(full_path, sound.file_path))
                        zf.write(full_path, arcname)
            else:
                # Single file
                arcname = os.path.join(category, os.path.basename(sound.file_path))
                zf.write(sound.file_path, arcname)

    # Compute zip size and checksum
    size_bytes = os.path.getsize(zip_filename)
    with open(zip_filename, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    # Create DB Pack record with all required fields
    pack = Pack(
        name=name,
        date=today_str,
        seed=int(datetime.today().strftime("%Y%m%d")),  # matches file selector seed
        zip_path=zip_filename,
        size_bytes=size_bytes,
        checksum=checksum,
        items=[sound.id for sound in selected_sounds.values()],
        status="generated",
        generated_by="file_selector",
        updated_at=datetime.now()
    )    
    db.add(pack)
    db.commit()

    logger.info(f"✅ Pack created at {zip_filename} with DB record ID {pack.id}")
    return zip_filename
