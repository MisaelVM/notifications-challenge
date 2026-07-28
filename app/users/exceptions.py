from fastapi import status

from app.core.exception_handlers import CustomException


class UsersException(CustomException):
    """Base exception for user-related errors."""


class UserNotFoundException(UsersException):
    def __init__(self, value: str, attribute: str = "id") -> None:
        super().__init__(
            error_code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with {attribute} '{value}' not found",
        )


class EmailAlreadyRegisteredException(UsersException):
    def __init__(self, email: str) -> None:
        super().__init__(
            error_code="EMAIL_ALREADY_REGISTERED",
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' is already associated with an account.",
        )
