import asyncio
import logging
import sys
from datetime import timedelta

from app import config
from app.api.routers import (
    users,
)
from app.api.security import clear_rate_limit_store
from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
)
from app.database.engine import get_db, init_db
from app.exceptions import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


init_db()
# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format="%(levelname)s: %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

app = FastAPI(title="Phonetica API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def every_10_minute_tasks():
    while True:
        await clear_rate_limit_store()
        await asyncio.sleep(10 * 60)  # 10 minutes


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(every_10_minute_tasks())


api = APIRouter(prefix="/api")
api.include_router(users.router, tags=["Users"])

app.include_router(api)


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    logger.error(f"NotFoundException in {request.url.path}: {exc}")
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    logger.error(f"BadRequestException in {request.url.path}: {exc}")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    logger.error(f"UnauthorizedException in {request.url.path}: {exc}")
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(InternalServerErrorException)
async def internal_server_error_exception_handler(
    request: Request, exc: InternalServerErrorException
):
    logger.error(f"InternalServerErrorException in {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"SQLAlchemyError in {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(TooManyRequestsException)
async def too_many_requests_exception_handler(
    request: Request, exc: TooManyRequestsException
):
    logger.error(f"TooManyRequestsException in {request.url.path}: {exc}")
    return JSONResponse(status_code=429, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Exception in {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.post("/token", tags=["System"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    email = form_data.username.lower().strip()
    password = form_data.password.strip()

    user = await authenticate_user(db, email, password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
