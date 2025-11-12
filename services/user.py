from db.mongo import getDB
from utils.common import verify_password

def login(id: str, pwd: str):
  if not id or not pwd:
    return None
  
  users = getDB("users")
  user = users.find_one({"id": id})

  if not user or not verify_password(pwd, user["password"]):
    return None
  
  return {"name": user["name"], "id": user["id"]}
  