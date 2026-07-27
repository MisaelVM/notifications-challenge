from fastapi import status

from app.core.exception_handlers import CustomException


class AuthException(CustomException):
    """Base exception for auth-related errors."""


class AuthenticationFailedException(AuthException):
    def __init__(self, message: str) -> None:
        super().__init__(
            error_code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(AuthException):
    def __init__(self) -> None:
        super().__init__(
            error_code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(AuthException):
    def __init__(self, action_description: str) -> None:
        super().__init__(
            error_code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You're not allowed to perform this action: {action_description}",
        )
