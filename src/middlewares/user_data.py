# middlewares/user_data.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_or_create_user
from database.models import User as DbUser


class UserDataMiddleware(BaseMiddleware):
    """
    This middleware retrieves or creates a user from the database
    and provides the User model instance to the handler.
    It depends on DbSessionMiddleware.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        raw_user = data.get("event_from_user")

        db: AsyncSession = data["db"]

        db_user: DbUser | None = None
        if raw_user:
            db_user = await get_or_create_user(
                db=db,
                telegram_id=raw_user.id,
                username=raw_user.username,
            )

        data["db_user"] = db_user

        return await handler(event, data)


# Экспортируем экземпляр
middleware = UserDataMiddleware()
