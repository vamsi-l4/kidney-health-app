import os, json, random
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-please")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

otp_store = {}

def _safe_load_users():
    """Avoids crash if users.json is empty or missing."""
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


def login(email: str, password: str):
    users = _safe_load_users()
    if email in users and pwd_context.verify(password, users[email]["password"]):
        token = create_access_token({"sub": email})
        user = {k: v for k, v in users[email].items() if k != "password"}
        return {"access_token": token, "token_type": "bearer", "user": user}
    raise HTTPException(status_code=401, detail="Invalid credentials")


def register(email: str, password: str, name: str):
    users = _safe_load_users()
    if email in users:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = pwd_context.hash(password)
    users[email] = {"password": hashed, "name": name}
    _save_users(users)
    token = create_access_token({"sub": email})
    user = {k: v for k, v in users[email].items() if k != "password"}
    return {"access_token": token, "token_type": "bearer", "user": user}


def forgot_password(email: str):
    users = _safe_load_users()
    if email not in users:
        raise HTTPException(status_code=400, detail="User not found")
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    print(f"OTP for {email}: {otp}")  # Debug log
    return {"message": "OTP sent to email"}


def verify_otp(email: str, otp: str):
    if email in otp_store and otp_store[email] == otp:
        del otp_store[email]
        return {"message": "OTP verified"}
    raise HTTPException(status_code=400, detail="Invalid OTP")


def reset_password(email: str, new_password: str):
    users = _safe_load_users()
    if email not in users:
        raise HTTPException(status_code=400, detail="User not found")
    hashed = pwd_context.hash(new_password)
    users[email]["password"] = hashed
    _save_users(users)
    return {"message": "Password reset successful"}
