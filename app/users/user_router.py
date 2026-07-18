from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.users.user_schema import UserCreate, UserResponse, UserUpdate
from app.users.user_service import UserService

router = APIRouter(prefix="/users")

type UserServiceDependency = Annotated[UserService, Depends()]


@router.get("", response_model=list[UserResponse])
async def get_users(service: UserServiceDependency):
    return await service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    service: UserServiceDependency,
):
    return await service.get_user(user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create_data: UserCreate,
    service: UserServiceDependency,
):
    return await service.create_user(user_create_data)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update_data: UserUpdate,
    service: UserServiceDependency,
):
    return await service.update_user(user_id, user_update_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    service: UserServiceDependency,
):
    return await service.delete_user(user_id)
