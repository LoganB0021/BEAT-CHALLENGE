from sqlalchemy import create_engine
from beat_challenge_generator.config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
