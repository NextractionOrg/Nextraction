import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.auth.models import User, UserCreate, UserResponse, Token, TokenData
from app.utils.logger import logger

# Get JWT settings from config
JWT_SECRET_KEY = settings.jwt_secret_key or os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = settings.jwt_algorithm
JWT_EXPIRATION_HOURS = settings.jwt_expiration_hours

# In-memory user storage (replace with database in production)
users_db: dict[str, User] = {}


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = settings.password_salt or os.getenv("PASSWORD_SALT", "default_salt_change_in_production")
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None:
            return None
        return TokenData(username=username, user_id=user_id)
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.JWTError as e:
        logger.warning(f"JWT error: {str(e)}")
        return None


def create_user(user_data: UserCreate) -> User:
    """Create a new user"""
    import uuid
    
    # Check if username or email already exists
    for user in users_db.values():
        if user.username == user_data.username:
            raise ValueError("Username already exists")
        if user.email == user_data.email:
            raise ValueError("Email already exists")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    users_db[user_id] = user
    logger.info(f"User created: {user.username}")
    return user


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password"""
    # Find user by username
    user = None
    for u in users_db.values():
        if u.username == username:
            user = u
            break
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by ID"""
    return users_db.get(user_id)


def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username"""
    for user in users_db.values():
        if user.username == username:
            return user
    return None

