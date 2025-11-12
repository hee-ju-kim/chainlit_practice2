import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  APP_NAME: str = "Chat App2"
  MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
  MONGO_DB: str = "chat_app"
  JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
  JWT_ALGORITHM: str = "HS256"
  JWT_EXPIRE_MINUTES: int = 60

settings = Settings()