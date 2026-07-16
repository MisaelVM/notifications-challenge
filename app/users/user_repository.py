from uuid import UUID, uuid4

from app.users.user_schema import UserCreate, UserResponse, UserUpdate

data: list[UserResponse] = []


class UserRepository:
    def __init__(self) -> None:
        self._db: list[UserResponse] = data

    def find_all(self) -> list[UserResponse]:
        return self._db

    def find_by_id(self, user_id: UUID) -> UserResponse | None:
        for user in self._db:
            if user.id == user_id:
                return user
        return None

    def create(self, create_data: UserCreate) -> UserResponse:
        new_user = UserResponse(
            id=uuid4(),
            name=create_data.name,
            email=create_data.email,
        )
        self._db.append(new_user)
        return new_user

    def update(self, user_id: UUID, update_data: UserUpdate) -> UserResponse | None:
        user = self.find_by_id(user_id)
        if user:
            items_to_update = update_data.model_dump(exclude_unset=True)
            for field, value in items_to_update.items():
                setattr(user, field, value)
            return user

    def delete(self, user_id: UUID) -> None:
        user = self.find_by_id(user_id)
        if user:
            self._db.remove(user)
