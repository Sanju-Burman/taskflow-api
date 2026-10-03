from typing import Annotated
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppException, UnauthorizedException
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repo import user_repo

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/oauth",
    auto_error=False,
)

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    db: SessionDep,
    token: TokenDep,
) -> User:
    """Validate bearer JWT token and return authenticated user."""
    if not token:
        raise UnauthorizedException("Authentication token required.")

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token.")

    token_type = payload.get("type")
    if token_type != "access":
        raise UnauthorizedException("Invalid token type for API authentication.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token payload missing subject.")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user identifier in token.")

    user = await user_repo.get(db, id=user_id)
    if not user:
        raise UnauthorizedException("User not found.")

    if not user.is_active:
        raise AppException(
            message="User account is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
