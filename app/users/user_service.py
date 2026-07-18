from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.users.user_repository import UserRepository
from app.users.user_schema import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self._user_repository: UserRepository = user_repository

    async def list_users(self) -> list[UserResponse]:
        users = await self._user_repository.find_all()
        return [UserResponse.model_validate(user) for user in users]

    async def get_user(self, user_id: UUID) -> UserResponse:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.model_validate(user)

    async def create_user(self, create_data: UserCreate) -> UserResponse:
        user = await self._user_repository.create(create_data)
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: UUID, update_data: UserUpdate) -> UserResponse:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self._user_repository.update(user, update_data)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self._user_repository.delete(user)
