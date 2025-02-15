import logging
from datetime import datetime, timedelta
from typing import Union

import httpx
from app import config
from app.api.models.users import LoginResponse, Token
from app.core.users import fetch_user_by_email
from app.database.engine import get_db
from app.database.schema.tokens import RefreshToken
from app.database.schema.users import User
from app.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Secret key for JWT signing and encoding
SECRET_KEY = config.SECRET_KEY
HASH_ALGORITHM = config.HASH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = config.REFRESH_TOKEN_EXPIRE_DAYS

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Create a utility function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Create a utility function to hash password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Create a utility function to create access tokens
def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=HASH_ALGORITHM)
    return encoded_jwt


# Create a utility function to get user by email
async def get_user(db: AsyncSession, email: str) -> Union[User, None]:
    user = await fetch_user_by_email(email, db)
    if user is None:
        raise NotFoundException("User not found")
    return user


# Authenticate user
async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Union[User, None]:
    user = await get_user(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def decode_access_token(token: str) -> Union[str, None]:
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASH_ALGORITHM])

        # Extract the subject (user's email in this case)
        email: str = payload.get("sub")

        # Return the decoded token data, particularly the email
        return email

    except JWTError as e:
        raise UnauthorizedException(f"Token is invalid or expired: {str(e)}")


# Function to get the current user based on the JWT token
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = UnauthorizedException("Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASH_ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    user = await get_user(db, email=email)
    if user is None:
        raise credentials_exception

    if user.last_active < (datetime.utcnow() - timedelta(days=1)).date():
        user.last_active = datetime.utcnow()
        db.add(user)
        await db.flush()
    return user


async def auth_login(
    response: Response, user: User, agent: str, db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    refresh_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    refresh_token_expires_at = datetime.utcnow() + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/users/refresh",
        secure=True,
        httponly=True,
        samesite="Strict",
    )

    # Check if a refresh token for this user and device already exists
    result = await db.execute(
        select(RefreshToken).filter_by(user_id=user.id, device_info=agent)
    )
    existing_token = result.scalars().first()

    if existing_token:
        # Update the existing token
        existing_token.token = refresh_token
        existing_token.issued_at = datetime.utcnow()
        existing_token.expires_at = refresh_token_expires_at
        db.add(existing_token)
    else:
        # Create a new token
        new_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            device_info=agent,
            issued_at=datetime.utcnow(),
            expires_at=refresh_token_expires_at,
        )
        db.add(new_refresh_token)

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    access_token_expire_days = 1 / (
        24 / (ACCESS_TOKEN_EXPIRE_MINUTES / 60)
    )  # Convert to days

    user.last_login = datetime.utcnow()
    db.add(user)
    await db.flush()

    return LoginResponse(
        email=user.email,
        name=user.name,
        timezone=user.timezone,
        last_login=user.last_login,
        access_token=Token(
            token=access_token,
            expires_days=access_token_expire_days,
        ),
    )


async def login_with_google(auth_code: str) -> tuple[str, str, bool]:
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "code": auth_code,
                "client_id": config.GOOGLE_CLIENT_ID,  # client ID from the credential at google developer console
                "client_secret": config.GOOGLE_SECRET_KEY,  # client secret from the credential at google developer console
                "redirect_uri": "postmessage",
                "grant_type": "authorization_code",
            }
            google_response = await client.post(
                "https://oauth2.googleapis.com/token", data=data
            )

            token_data = google_response.json()
            google_access_token = token_data["access_token"]

            headers = {"Authorization": f"Bearer {google_access_token}"}

            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
            )

            user_info = user_info_response.json()

            email = user_info.get("email")
            name = user_info.get("name")
            email_verified = user_info.get("email_verified")

            return email, name, email_verified
    except KeyError as e:
        raise BadRequestException(f"Missing key: {str(e)}")
    except JWTError:
        raise UnauthorizedException("Invalid token")
