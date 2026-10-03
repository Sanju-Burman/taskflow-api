from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate
from app.core.security import hash_password


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        query = select(User).where(User.email == email.lower())
        result = await db.execute(query)
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, *, user_in: UserCreate) -> User:
        user_dict = {
            "email": user_in.email.lower(),
            "hashed_password": hash_password(user_in.password),
            "full_name": user_in.full_name,
            "is_active": True,
            "is_superuser": False,
        }
        return await self.create(db, obj_in=user_dict)


user_repo = UserRepository()
