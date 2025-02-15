from app.database.schema.users import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def fetch_user_by_email(email: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).filter(User.email == email.lower().strip()))
    return result.scalars().first()
