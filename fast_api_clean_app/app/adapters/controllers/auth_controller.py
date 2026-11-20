from fastapi import APIRouter, Depends, HTTPException, status

from app.use_cases.register_user import RegisterUserUseCase, RegisterUserCommand
from app.use_cases.authenticate_with_password import (
    AuthenticateWithPasswordUseCase, AuthenticateWithPasswordCommand,
)
from app.adapters.controllers.schemas import RegisterRequest, LoginRequest
from app.adapters.controllers.dependencies import (
    get_register_use_case,
    get_login_use_case,
)
from app.domain.exceptions import (
    EmailAlreadyTakenError, InvalidCredentialsError,
    PlayerInactiveError, WeakPasswordError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    try:
        result = await use_case.execute(
            RegisterUserCommand(body.email, body.password, body.display_name)
        )
    except EmailAlreadyTakenError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, exc.message)
    except WeakPasswordError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.message)
    return {
        "player_id": result.player_id,
        "access_token": result.tokens.access_token,
        "refresh_token": result.tokens.refresh_token,
        "token_type": result.tokens.token_type,
        "expires_in": result.tokens.expires_in,
    }


@router.post("/login")
async def login(
    body: LoginRequest,
    use_case: AuthenticateWithPasswordUseCase = Depends(get_login_use_case),
):
    try:
        result = await use_case.execute(
            AuthenticateWithPasswordCommand(body.email, body.password)
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, exc.message)
    except PlayerInactiveError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, exc.message)
    return {
        "player_id": result.player_id,
        "access_token": result.tokens.access_token,
        "refresh_token": result.tokens.refresh_token,
        "token_type": result.tokens.token_type,
        "expires_in": result.tokens.expires_in,
    }
