# server/app/auth.py
import os
import json
import random
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-please")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

otp_store = {}

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def login(email: str, password: str):
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if email in users and users[email]['password'] == password:
        token = create_access_token({"sub": email})
        return {"access_token": token, "token_type": "bearer", "user": users[email]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

def register(email: str, password: str, name: str):
    with open(USERS_FILE, 'r+') as f:
        users = json.load(f)
        if email in users:
            raise HTTPException(status_code=400, detail="User already exists")
        users[email] = {"password": password, "name": name}
        f.seek(0)
        json.dump(users, f)
        f.truncate()
    token = create_access_token({"sub": email})
    return {"access_token": token, "token_type": "bearer", "user": users[email]}

def forgot_password(email: str):
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    if email not in users:
        raise HTTPException(status_code=400, detail="User not found")
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    # In real app, send email with OTP
    print(f"OTP for {email}: {otp}")  # For testing
    return {"message": "OTP sent to email"}

def verify_otp(email: str, otp: str):
    if email in otp_store and otp_store[email] == otp:
        del otp_store[email]
        return {"message": "OTP verified"}
    raise HTTPException(status_code=400, detail="Invalid OTP")

def reset_password(email: str, new_password: str):
    with open(USERS_FILE, 'r+') as f:
        users = json.load(f)
        if email not in users:
            raise HTTPException(status_code=400, detail="User not found")
        users[email]['password'] = new_password
        f.seek(0)
        json.dump(users, f)
        f.truncate()
    return {"message": "Password reset successful"}
