from uuid import UUID

from fastapi import APIRouter, status

from app.auth.service import CurrentUser
from app.users.schemas import UserPrivate, UserPublic, UserUpdate
from app.users.service import UserServiceDependency

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: UUID,
    service: UserServiceDependency,
):
    return await service.get_user_by_id(user_id)


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: UUID,
    user_update_data: UserUpdate,
    current_user: CurrentUser,
    service: UserServiceDependency,
):
    return await service.update_user(user_id, user_update_data, current_user.id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser,
    service: UserServiceDependency,
):
    return await service.delete_user(user_id, current_user.id)
