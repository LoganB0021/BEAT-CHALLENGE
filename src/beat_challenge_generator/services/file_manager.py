from datetime import datetime
import hashlib
import os

from sqlalchemy.orm import Session
from beat_challenge_generator.logging.logger import logger
from beat_challenge_generator.config import OUTPUT_DIR
from beat_challenge_generator.models import Pack
from beat_challenge_generator.utils.zip_utils import write_sounds_zip


def create_pack(selected_sounds: dict, session: Session):
    """
    Create a Pack record in DB and write zip to OUTPUT_DIR.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Deterministic name based on date
    today_str = datetime.today().strftime("%Y-%m-%d")
    name = f"pack_{today_str}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(OUTPUT_DIR, f"pack_{timestamp}.zip")

    # Write the zip using the utility
    write_sounds_zip(selected_sounds, zip_path)

    # Compute zip size and checksum
    size_bytes = os.path.getsize(zip_path)
    with open(zip_path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    # Insert Pack record
    pack = Pack(
        name=name,
        date=today_str,
        seed=int(datetime.today().strftime("%Y%m%d")),
        zip_path=zip_path,
        size_bytes=size_bytes,
        checksum=checksum,
        items=[sound.id for sound in selected_sounds.values()],
        status="generated",
        generated_by="file_selector",
        updated_at=datetime.now()
    )
    session.add(pack)
    session.commit()

    logger.info(f"✅ Pack created at {zip_path} with DB record ID {pack.id}")
    return zip_path