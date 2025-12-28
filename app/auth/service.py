import os
import json
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
from app.auth.models import User, UserCreate, UserResponse, Token, TokenData
from app.utils.logger import logger

# Get JWT settings from config
JWT_ALGORITHM = getattr(settings, 'jwt_algorithm', 'HS256')
JWT_EXPIRATION_HOURS = getattr(settings, 'jwt_expiration_hours', 24)

# File paths for persistent storage
USERS_DB_FILE = os.path.join(settings.data_dir, "users.json")
SALT_FILE = os.path.join(settings.data_dir, ".salt")
JWT_SECRET_FILE = os.path.join(settings.data_dir, ".jwt_secret")

# In-memory user storage (loaded from file)
users_db: dict[str, User] = {}

# Password salt (must be persistent)
_password_salt = None

# JWT Secret Key (must be persistent)
_jwt_secret_key = None


def _get_jwt_secret_key() -> str:
    """Get or create a persistent JWT secret key"""
    global _jwt_secret_key
    
    if _jwt_secret_key:
        return _jwt_secret_key
    
    # Try to get from config/env first
    secret = getattr(settings, 'jwt_secret_key', None) or os.getenv("JWT_SECRET_KEY")
    
    if secret:
        _jwt_secret_key = secret
        return secret
    
    # Try to load from file
    try:
        os.makedirs(settings.data_dir, exist_ok=True)
        if os.path.exists(JWT_SECRET_FILE):
            with open(JWT_SECRET_FILE, 'r') as f:
                _jwt_secret_key = f.read().strip()
                return _jwt_secret_key
    except Exception as e:
        logger.warning(f"Could not load JWT secret from file: {str(e)}")
    
    # Generate new secret and save it
    _jwt_secret_key = secrets.token_urlsafe(64)
    try:
        os.makedirs(settings.data_dir, exist_ok=True)
        with open(JWT_SECRET_FILE, 'w') as f:
            f.write(_jwt_secret_key)
        logger.info("Generated and saved new JWT secret key")
    except Exception as e:
        logger.error(f"Could not save JWT secret to file: {str(e)}")
    
    return _jwt_secret_key




def _ensure_users_file():
    """Ensure the users database file exists"""
    os.makedirs(settings.data_dir, exist_ok=True)
    if not os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, 'w') as f:
            json.dump({}, f)


def _load_users():
    """Load users from JSON file"""
    global users_db
    try:
        _ensure_users_file()
        if os.path.exists(USERS_DB_FILE) and os.path.getsize(USERS_DB_FILE) > 0:
            with open(USERS_DB_FILE, 'r') as f:
                data = json.load(f)
                users_db = {}
                for user_id, user_data in data.items():
                    # Convert datetime string back to datetime object
                    user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    users_db[user_id] = User(**user_data)
                logger.info(f"Loaded {len(users_db)} users from database")
        else:
            users_db = {}
            logger.info("No existing users database found, starting fresh")
    except Exception as e:
        logger.error(f"Error loading users: {str(e)}")
        users_db = {}


def _save_users():
    """Save users to JSON file"""
    try:
        _ensure_users_file()
        data = {}
        for user_id, user in users_db.items():
            user_dict = user.model_dump()
            # Convert datetime to ISO format string for JSON serialization
            user_dict['created_at'] = user.created_at.isoformat()
            data[user_id] = user_dict
        with open(USERS_DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved {len(users_db)} users to database")
    except Exception as e:
        logger.error(f"Error saving users: {str(e)}")


# Load users on module import
_load_users()


def _get_password_salt() -> str:
    """Get or create a persistent password salt"""
    global _password_salt
    
    if _password_salt:
        return _password_salt
    
    # Try to get from config/env first
    salt = getattr(settings, 'password_salt', None) or os.getenv("PASSWORD_SALT")
    
    if salt:
        _password_salt = salt
        return salt
    
    # Try to load from file
    try:
        os.makedirs(settings.data_dir, exist_ok=True)
        if os.path.exists(SALT_FILE):
            with open(SALT_FILE, 'r') as f:
                _password_salt = f.read().strip()
                return _password_salt
    except Exception as e:
        logger.warning(f"Could not load salt from file: {str(e)}")
    
    # Generate new salt and save it
    _password_salt = secrets.token_urlsafe(32)
    try:
        os.makedirs(settings.data_dir, exist_ok=True)
        with open(SALT_FILE, 'w') as f:
            f.write(_password_salt)
        logger.info("Generated and saved new password salt")
    except Exception as e:
        logger.error(f"Could not save salt to file: {str(e)}")
    
    return _password_salt


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = _get_password_salt()
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
    secret_key = _get_jwt_secret_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and verify a JWT token"""
    try:
        secret_key = _get_jwt_secret_key()
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
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
    _save_users()  # Persist to file
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

