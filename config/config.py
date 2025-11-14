import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
  APP_NAME: str = "Chat App2"
  MONGO_URI: str = os.getenv("DATABASE")
  MONGO_DB: str = "chat_app"
  JWT_SECRET: str = os.getenv("JWT_SECRET")
  JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
  JWT_EXPIRE_MINUTES: int = 60
  S3_BUCKET: str = os.getenv("BUCKET_NAME")

settings = Settings()