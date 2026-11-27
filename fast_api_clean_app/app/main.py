from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from app.adapters.controllers.auth_controller import router as auth_router
from app.config import settings
from app.domain.exceptions import (
    DomainError,
    PlatformAlreadyLinkedError,
    PlatformAlreadyLinkedToAnotherPlayerError,
    EmailAlreadyTakenError,
    InvalidCredentialsError,
    PlayerInactiveError,
    WeakPasswordError,
    InvalidEmailError,
    InvalidPasswordHashError,
)
from app.infrastructure.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)


app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)


app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def index():
    return FileResponse("frontend/index.html")


_STATUS_BY_ERROR = {
    PlatformAlreadyLinkedError: 409,
    PlatformAlreadyLinkedToAnotherPlayerError: 409,
    EmailAlreadyTakenError: 409,
    WeakPasswordError: 422,
    InvalidEmailError: 422,
    InvalidPasswordHashError: 422,
    InvalidCredentialsError: 401,
    PlayerInactiveError: 403,
}


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    status_code = _STATUS_BY_ERROR.get(type(exc), 400)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )
