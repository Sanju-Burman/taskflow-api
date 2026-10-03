from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.repositories.user_repo import user_repo
from app.schemas.user import Token, UserCreate, UserLogin, UserWithToken


class UserService:
    async def register(self, db: AsyncSession, *, user_in: UserCreate) -> UserWithToken:
        existing_user = await user_repo.get_by_email(db, email=user_in.email)
        if existing_user:
            raise ConflictException("A user with this email address already exists.")

        user = await user_repo.create_user(db, user_in=user_in)
        token = self._generate_auth_tokens(user.id)
        return UserWithToken(user=user, token=token)

    async def authenticate(self, db: AsyncSession, *, login_data: UserLogin) -> UserWithToken:
        user = await user_repo.get_by_email(db, email=login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is disabled.")

        token = self._generate_auth_tokens(user.id)
        return UserWithToken(user=user, token=token)

    async def get_by_id(self, db: AsyncSession, *, user_id: int) -> User:
        user = await user_repo.get(db, id=user_id)
        if not user:
            raise NotFoundException("User not found.")
        return user

    def _generate_auth_tokens(self, user_id: int) -> Token:
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )


user_service = UserService()
