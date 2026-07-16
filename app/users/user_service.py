from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.users.user_repository import UserRepository
from app.users.user_schema import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self._user_repository: UserRepository = user_repository

    def list_users(self) -> list[UserResponse]:
        return self._user_repository.find_all()

    def get_user(self, user_id: UUID) -> UserResponse:
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def create_user(self, create_data: UserCreate) -> UserResponse:
        return self._user_repository.create(create_data)

    def update_user(self, user_id: UUID, update_data: UserUpdate) -> UserResponse:
        user = self._user_repository.update(user_id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def delete_user(self, user_id: UUID) -> None:
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        self._user_repository.delete(user_id)
