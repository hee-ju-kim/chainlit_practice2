from typing import Optional
from pymongo import MongoClient
from chainlit.data.base import BaseDataLayer
from config.config import settings

class MongoDataLayer(BaseDataLayer):
    def __init__(self, uri: str = settings.MONGO_URI, db_name: str = settings.MONGO_DB):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users = self.db["users"]
        self.messages = self.db["messages"]

    # 사용자 가져오기
    def get_user(self, user_id: str) -> Optional[dict]:
        return self.users.find_one({"user_id": user_id})

    # 사용자 생성
    def create_user(self, user_id: str, user_data: dict) -> dict:
        user_data["user_id"] = user_id
        self.users.insert_one(user_data)
        return user_data

    # 메시지 저장
    def persist_message(self, user_id: str, message: dict):
        message["user_id"] = user_id
        self.messages.insert_one(message)

    # 메시지 가져오기
    def get_messages(self, user_id: str):
        return list(self.messages.find({"user_id": user_id}))
