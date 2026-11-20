from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.adapters.controllers.auth_controller import router as auth_router
from app.domain.exceptions import (
    DomainError,
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


_STATUS_BY_ERROR = {
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
