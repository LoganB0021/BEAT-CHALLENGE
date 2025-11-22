from datetime import date
from beat_challenge_generator.db import get_session
from beat_challenge_generator.logger import logger
import beat_challenge_generator.config
from beat_challenge_generator.file_selector import deterministic_select_by_date
from beat_challenge_generator.file_manager import create_pack
from beat_challenge_generator.models import Pack
import os

def main(dry_run: bool = False):
    logger.info("🎵 Starting Beat Challenge Generator...")

    try:
        today_str = date.today().isoformat()
        
        with get_session() as db:
            # Check if today's pack already exists
            existing_pack = db.query(Pack).filter(Pack.date == today_str).first()
            
            if existing_pack:
                logger.info(f"💡 Pack for {today_str} already exists: {existing_pack.zip_path}")
                print(f"🎵 Today's beat challenge already exists: {existing_pack.zip_path}")

                # Ask user for permission to overwrite
                response = input("Do you want to overwrite it? (y/N): ").strip().lower()
                if response != "y":
                    print("❌ Exiting without overwriting.")
                    return
                
                # Delete the existing pack
                logger.info(f"🗑️ Deleting existing pack {existing_pack.zip_path}")
                
                # Remove zip file if it exists
                if existing_pack.zip_path and os.path.exists(existing_pack.zip_path):
                    os.remove(existing_pack.zip_path)
                    logger.info(f"Deleted file: {existing_pack.zip_path}")
                
                db.delete(existing_pack)
                db.commit()
                logger.info("Deleted existing DB entry.")

            # Select files deterministically
            selected = deterministic_select_by_date(db)
            logger.info(f"Selected files: {selected}")

            # Create the new pack
            zip_path = create_pack(selected, db)
            logger.info(f"🎵 Beat challenge created: {zip_path}")
            print(f"🎵 Beat challenge created: {zip_path}")

    except Exception as e:
        logger.error(f"🚨 An error occurred: {e}")

if __name__ == "__main__":
    main(dry_run=False)
