import hmac
import json
import os
import random
import re
import tempfile
import threading
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

# Older versions of this application stored bcrypt hashes and, unfortunately,
# a few development accounts with plain-text passwords.  Supporting both hash
# formats lets existing users sign in; a successful legacy sign-in is upgraded
# to PBKDF2 immediately below.
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-please")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

otp_store = {}
users_lock = threading.Lock()
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def _safe_load_users():
    """Avoids crash if users.json is empty or missing."""
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
            return users if isinstance(users, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

def _save_users(users):
    """Persist data atomically so an interrupted write cannot corrupt users."""
    fd, temporary_path = tempfile.mkstemp(
        dir=os.path.dirname(USERS_FILE), prefix="users-", suffix=".json"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)
        os.replace(temporary_path, USERS_FILE)
    except OSError:
        try:
            os.unlink(temporary_path)
        except OSError:
            pass
        raise


def _validate_credentials(email: str, password: str, name: str | None = None):
    normalized_email = (email or "").strip().lower()
    normalized_name = name.strip() if name else name
    if not EMAIL_PATTERN.fullmatch(normalized_email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    if not password or len(password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters long")
    if name is not None and (not normalized_name or len(normalized_name) < 2):
        raise HTTPException(status_code=422, detail="Name must be at least 2 characters long")
    return normalized_email, normalized_name


def _public_user(email: str, user: dict):
    return {"email": email, **{key: value for key, value in user.items() if key != "password"}}


def _password_matches(password: str, stored_password: str) -> bool:
    if not isinstance(stored_password, str):
        return False
    if stored_password.startswith("$"):
        try:
            return pwd_context.verify(password, stored_password)
        except (ValueError, TypeError):
            return False
    # Compatibility only for old local development data. Never create these.
    return hmac.compare_digest(password, stored_password)


def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=(expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


def login(email: str, password: str):
    normalized_email, _ = _validate_credentials(email, password)
    with users_lock:
        users = _safe_load_users()
        user = users.get(normalized_email)
        if not user or not _password_matches(password, user.get("password")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user["password"].startswith("$") or pwd_context.needs_update(user["password"]):
            user["password"] = pwd_context.hash(password)
            _save_users(users)
    token = create_access_token({"sub": normalized_email})
    return {"access_token": token, "token_type": "bearer", "user": _public_user(normalized_email, user)}


def register(email: str, password: str, name: str):
    normalized_email, normalized_name = _validate_credentials(email, password, name)
    with users_lock:
        users = _safe_load_users()
        if normalized_email in users:
            raise HTTPException(status_code=409, detail="An account already exists for this email")
        users[normalized_email] = {
            "password": pwd_context.hash(password),
            "name": normalized_name,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        _save_users(users)
        user = users[normalized_email]
    token = create_access_token({"sub": normalized_email})
    return {"access_token": token, "token_type": "bearer", "user": _public_user(normalized_email, user)}


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
