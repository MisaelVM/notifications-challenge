import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID, default=uuid.uuid4, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        sa.String(120), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(sa.String(200), nullable=False)
