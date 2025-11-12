
from cryptography.fernet import Fernet
from config.config import settings
import base64
import hashlib

# 키 생성
def generate_fernet_key(secret_key: str) -> bytes:
  # SHA256으로 32바이트 해시 생성 후 base64로 인코딩
  key = hashlib.sha256(secret_key.encode()).digest()
  return base64.urlsafe_b64encode(key)

FERNET_KEY = generate_fernet_key(settings.JWT_SECRET)
fernet = Fernet(FERNET_KEY)

# 암호화
def hash_password(password: str) -> str:
  token = fernet.encrypt(password.encode())
  return token.decode()

# 검증
def verify_password(password: str, hashed: str) -> bool:
  try:
    decrypted = fernet.decrypt(hashed.encode()).decode()
    return decrypted == password
  except:
    return False