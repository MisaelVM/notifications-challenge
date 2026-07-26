from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import RegisterUserRequest, Token
from app.auth.service import AuthServiceDependency
from app.users.schemas import UserResponse

router = APIRouter(prefix="/auth")


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create_data: RegisterUserRequest, auth_service: AuthServiceDependency
):
    return await auth_service.register_user(user_create_data)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDependency,
):
    return await auth_service.login_for_access_token(form_data)
