import logging
import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.exceptions import (
    AuthenticationFailedException,
    InvalidCredentialsException,
)
from app.auth.schemas import RegisterUserRequest, Token
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
)
from app.users.exceptions import EmailAlreadyRegisteredException
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserPublic
from app.users.service import UserService, UserServiceDependency

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_service: UserServiceDependency) -> None:
        self._user_service: UserService = user_service

    async def register_user(
        self,
        register_user_data: RegisterUserRequest,
    ) -> UserPublic:
        email_exists = await self._user_service.is_email_already_registered(
            register_user_data.email
        )
        if email_exists:
            raise EmailAlreadyRegisteredException(email=register_user_data.email)

        new_user = UserCreate(
            name=register_user_data.name,
            email=register_user_data.email,
            password_hash=hash_password(register_user_data.password),
        )
        return await self._user_service.create_user(new_user)

    async def login_for_access_token(
        self,
        form_data: OAuth2PasswordRequestForm,
    ) -> Token:
        user = await self._user_service.get_user_by_email_internal(form_data.username)
        if not user or not verify_password(form_data.password, user.password_hash):
            logger.warning(
                "Failed login attempt for %s: %s",
                form_data.username,
                "Wrong password" if user else "Email does not exist",
            )
            raise InvalidCredentialsException

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")  # noqa: S106


type AuthServiceDependency = Annotated[AuthService, Depends()]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: Annotated[UserRepository, Depends()],
) -> User:
    user_id = verify_access_token(token)
    if user_id is None:
        logger.warning("Token verification failed.")
        raise AuthenticationFailedException(message="Invalid or expired token.")

    try:
        user_id_as_uuid = uuid.UUID(user_id)
    except (TypeError, ValueError) as MalformedPayloadError:
        logger.warning("JWT 'sub' property is not a valid UUID: %s", user_id)
        raise AuthenticationFailedException(
            message="Invalid or expired token."
        ) from MalformedPayloadError

    user = await user_repository.find_by_id(user_id_as_uuid)
    if not user:
        logger.warning("Authenticated user %s not found in database.", user_id_as_uuid)
        raise AuthenticationFailedException(message="Invalid or expired token.")
    return user


type CurrentUser = Annotated[User, Depends(get_current_user)]
