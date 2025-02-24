from file_selector import generate_beat_challenge
from file_manager import create_beat_pack
from logger import logger

def main():
    """Main function to generate a beat challenge."""
    logger.info("Starting Beat Challenge Generator...")

    selected_files = generate_beat_challenge()
    if selected_files:
        zip_path = create_beat_pack(selected_files)
        if zip_path:
            logger.info(f"Beat challenge ready: {zip_path}")
            print(f"🎵 Beat challenge created: {zip_path}")
        else:
            logger.error("Failed to create beat challenge pack.")
    else:
        logger.error("No files selected for beat challenge.")

if __name__ == "__main__":
    main()
