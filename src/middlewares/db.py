# middlewares/db.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.database import AsyncSessionLocal

class DbSessionMiddleware(BaseMiddleware):
    """
    This middleware provides an SQLAlchemy session to the handler.
    It ensures that the session is properly opened and closed.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data["db"] = session
            return await handler(event, data)

priority = 10
middleware = DbSessionMiddleware()