import logging
from datetime import datetime, timedelta

from app.api.models.users import (
    ChangePasswordRequest,
    EditUserRequest,
    GoogleLoginRequest,
    LoginRequest,
    LoginResponse,
    SignupRequest,
    Token,
    UserInDB,
)
from app.api.security import rate_limiter
from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    auth_login,
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_password_hash,
    login_with_google,
)
from app.core.users import fetch_user_by_email
from app.database.engine import get_db
from app.database.schema.tokens import RefreshToken
from app.database.schema.users import User
from app.email import send_welcome_email
from app.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Header,
    Request,
    Response,
)
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users")


@router.get("/whoami", response_model=UserInDB)
@router.get("/whoami/", response_model=UserInDB, include_in_schema=False)
async def get_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/signup",
    response_model=UserInDB,
    dependencies=[Depends(rate_limiter)],
)
@router.post(
    "/signup/",
    response_model=UserInDB,
    include_in_schema=False,
)
async def post_signup(
    signup_request: SignupRequest,
    db: AsyncSession = Depends(get_db),
    x_timezone: str = Header(..., description="User's timezone"),
):
    email = signup_request.email.lower().strip()
    name = signup_request.name.strip()
    password = signup_request.password.strip()

    user = await fetch_user_by_email(email, db)
    if user:
        raise BadRequestException("Email already registered")

    new_user = User(
        email=email,
        name=name,
        password_hash=get_password_hash(password),
        timezone=x_timezone,
        last_login=datetime.utcnow(),
    )
    db.add(new_user)
    await db.flush()

    # Send welcome email
    await send_welcome_email(new_user.email, new_user.name)

    return new_user


@router.post(
    "/login",
    response_model=LoginResponse,
    dependencies=[Depends(rate_limiter)],
)
@router.post(
    "/login/",
    response_model=LoginResponse,
    include_in_schema=False,
)
async def post_login(
    login_request: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    x_timezone: str = Header(..., description="User's timezone"),
):
    email = login_request.email.lower().strip()
    password = login_request.password.strip()

    user = await authenticate_user(db, email, password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    device_info = request.headers.get("user-agent")

    user.timezone = x_timezone

    return await auth_login(response, user, device_info, db)


@router.post(
    "/login/google",
    response_model=LoginResponse,
    dependencies=[Depends(rate_limiter)],
)
@router.post(
    "/login/google/",
    response_model=LoginResponse,
    include_in_schema=False,
)
async def post_google_login(
    google_request: GoogleLoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    x_timezone: str = Header(..., description="User's timezone"),
):
    email, name, email_verified = await login_with_google(google_request.code)

    if not email or not email_verified:
        raise BadRequestException("Email not verified")

    # Check if the user exists
    user = await fetch_user_by_email(email, db)

    if not user:
        user = User(
            email=email,
            name=name,
            timezone=x_timezone,
            last_login=datetime.utcnow(),
        )
        db.add(user)
        await db.flush()
        # Send welcome email for new Google users
        await send_welcome_email(user.email, user.name)
    else:
        # Remove users password hash
        user.password_hash = None
        user.timezone = x_timezone

    device_info = request.headers.get("user-agent")

    return await auth_login(response, user, device_info, db)


@router.get(
    "/refresh",
    response_model=Token,
    dependencies=[Depends(rate_limiter)],
)
@router.get(
    "/refresh/",
    response_model=Token,
    include_in_schema=False,
)
async def get_refresh_token(
    refresh_token: str = Cookie(None, alias="refreshToken"),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        raise UnauthorizedException("Refresh token is missing")

    try:
        # Decode the refresh token
        email = decode_access_token(refresh_token)
        if email is None:
            raise UnauthorizedException("Invalid token")

        # Get the user from the database
        user = await fetch_user_by_email(email, db)
        if not user:
            raise NotFoundException("User not found")

        # Check if the refresh token exists in the database
        result = await db.execute(
            select(RefreshToken).filter_by(user_id=user.id, token=refresh_token)
        )
        existing_token = result.scalars().first()

        if not existing_token:
            raise UnauthorizedException("Invalid token")

        # Generate a new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        access_token_expire_days = 1 / (
            24 / (ACCESS_TOKEN_EXPIRE_MINUTES / 60)
        )  # Convert to days

        return Token(
            token=access_token,
            expires_days=access_token_expire_days,
        )

    except JWTError:
        raise UnauthorizedException("Invalid token")


@router.put("", response_model=UserInDB)
@router.put("/", response_model=UserInDB, include_in_schema=False)
async def put_user(
    user: EditUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user.name is not None:
        current_user.name = user.name.strip()
    if user.timezone is not None:
        current_user.timezone = user.timezone
    if user.native_language_code is not None:
        current_user.native_language_code = user.native_language_code

    db.add(current_user)
    await db.flush()

    return current_user


@router.put("/password")
@router.put("/password/", include_in_schema=False)
async def put_change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await authenticate_user(
        db, current_user.email, request.current_password.strip()
    )
    if not user:
        return {"message": "Incorrect password"}
    current_user.password_hash = get_password_hash(request.new_password.strip())

    db.add(current_user)

    return {"message": "Password updated successfully"}


@router.post("/logout")
@router.post("/logout/", include_in_schema=False)
async def post_logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device_info = request.headers.get("user-agent")
    if not device_info:
        raise BadRequestException("Device info is missing")

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.device_info == device_info,
        )
    )
    refresh_token = result.scalars().first()

    if not refresh_token:
        raise BadRequestException("Refresh token is missing")

    # Remove the refresh token from the database
    await db.delete(refresh_token)

    # Remove the refresh token cookie
    response.delete_cookie(
        key="refreshToken",
        path="/api/users/refresh",
        secure=True,
        httponly=True,
        samesite="Strict",
    )

    return {"message": "Logged out successfully"}
