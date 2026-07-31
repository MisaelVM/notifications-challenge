from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import RegisterUserRequest, Token
from app.auth.service import AuthServiceDependency
from app.core.rate_limiter import limiter
from app.users.schemas import UserPrivate

router = APIRouter(prefix="/auth")


@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/15 minutes")
async def register_user(
    user_create_data: RegisterUserRequest,
    auth_service: AuthServiceDependency,
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
):
    return await auth_service.register_user(user_create_data)


@router.post("/token", response_model=Token)
@limiter.limit("5/15 minutes")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDependency,
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
):
    return await auth_service.login_for_access_token(form_data)
