from pymongo import MongoClient

from config.config import settings
from utils.common import hash_password
import atexit

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

# 실행시 디비 초기화
def init_db():
  users_collection = db["users"]
  admin_username = "admin"
  admin_password = "1234"
  admin_user = users_collection.find_one({"id": admin_username})

  if not admin_user:
    hashed_pw = hash_password(admin_password)
    users_collection.insert_one({"id": admin_username, "password": hashed_pw, "name": "최고관리자"})
    print(f"[MongoDB] 관리자 계정 '{admin_username}' 생성 완료")

def getDB(name: str):
  return db[name]

# 종료 시 MongoDB 연결 해제
def close_db_connection():
  print("🛑 MongoDB 연결 종료")
  client.close()

# 종료 시 자동으로 연결 해제
atexit.register(close_db_connection)