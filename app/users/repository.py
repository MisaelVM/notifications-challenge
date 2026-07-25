from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.users.models import User
from app.users.schema import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db_session)]) -> None:
        self._db: AsyncSession = db

    async def find_all(self) -> Sequence[User]:
        result = await self._db.execute(select(User))
        return result.scalars().all()

    async def find_by_id(self, user_id: UUID) -> User | None:
        return await self._db.get(User, user_id)

    async def create(self, create_data: UserCreate) -> User:
        # TODO: Handle db constraints exceptions for insert
        # TODO: Hash password
        new_user = User(
            name=create_data.name,
            email=create_data.email,
            password_hash=create_data.password,
        )
        self._db.add(new_user)
        await self._db.commit()
        await self._db.refresh(new_user)
        return new_user

    async def update(self, user: User, update_data: UserUpdate) -> None:
        data_to_update = update_data.model_dump(exclude_unset=True)
        for field, value in data_to_update.items():
            setattr(user, field, value)
        await self._db.commit()
        await self._db.refresh(user)

    async def delete(self, user: User) -> None:
        await self._db.delete(user)
        await self._db.commit()
