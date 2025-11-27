import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://beat:beatpass@localhost:5432/beatdb")

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minio")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minio123")
S3_BUCKET = "beat-challenges"
