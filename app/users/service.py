from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import EmailStr

from app.auth.exceptions import PermissionDeniedException
from app.users.exceptions import EmailAlreadyRegisteredException, UserNotFoundException
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserPrivate, UserPublic, UserUpdate

if TYPE_CHECKING:
    from app.users.models import User


class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self._user_repository: UserRepository = user_repository

    async def list_users(self) -> list[UserPublic]:
        users = await self._user_repository.find_all()
        return [UserPublic.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: UUID) -> UserPrivate:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))

        return UserPrivate.model_validate(user)

    async def get_user_by_email_internal(self, email: EmailStr) -> User | None:
        return await self._user_repository.find_by_email(email)

    async def get_user_by_email(self, email: EmailStr) -> UserPrivate:
        user = await self.get_user_by_email_internal(email)
        if not user:
            raise UserNotFoundException(value=email, attribute="email")

        return UserPrivate.model_validate(user)

    async def is_email_already_registered(self, email: EmailStr) -> bool:
        user = await self._user_repository.find_by_email(email)
        return user is not None

    async def create_user(self, create_data: UserCreate) -> UserPrivate:
        if await self.is_email_already_registered(create_data.email):
            raise EmailAlreadyRegisteredException(create_data.email)

        user = await self._user_repository.create(create_data)
        return UserPrivate.model_validate(user)

    async def update_user(
        self, user_id: UUID, update_data: UserUpdate, actor_id: UUID
    ) -> UserPrivate:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))

        if user_id != actor_id:
            raise PermissionDeniedException(
                action_description="Modify someone else's profile."
            )

        await self._user_repository.update(user, update_data)
        return UserPrivate.model_validate(user)

    async def delete_user(self, user_id: UUID, actor_id: UUID) -> None:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))

        if user_id != actor_id:
            raise PermissionDeniedException(
                action_description="Delete someone else's profile."
            )

        await self._user_repository.delete(user)


type UserServiceDependency = Annotated[UserService, Depends()]
