from beat_challenge_generator.logger import logger  # Initialize logger first
import beat_challenge_generator.config  # Ensure config runs early (creates directories)
from beat_challenge_generator.file_selector import generate_beat_challenge
from beat_challenge_generator.file_manager import create_beat_pack

def main():
    """Main function to generate a beat challenge."""
    logger.info("🎵 Starting Beat Challenge Generator...")

    try:
        # Step 1: Select random beat components
        selected_files = generate_beat_challenge()
        
        if selected_files:
            logger.info(f"✅ Selected files: {selected_files}")

            # Step 2: Create a zip file with the selected files
            zip_path = create_beat_pack(selected_files)

            if zip_path:
                logger.info(f"🎉 Beat challenge ready: {zip_path}")
                print(f"🎵 Beat challenge created: {zip_path}")
            else:
                logger.error("❌ Failed to create beat challenge pack.")
        else:
            logger.error("⚠️ No files selected for beat challenge.")

    except Exception as e:
        logger.error(f"🚨 An error occurred: {e}")

if __name__ == "__main__":
    main()
