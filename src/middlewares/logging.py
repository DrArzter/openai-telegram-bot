# middlewares/logging.py
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_name = "unknown"
        user_id = "unknown"
        command = None
        event_type = type(event).__name__

        message = getattr(event, "message", None) or getattr(
            event, "edited_message", None
        )
        if isinstance(message, Message):
            user = message.from_user
            user_name = user.username if user else "unknown"
            user_id = user.id if user else "unknown"

            command = None
            if message.entities:
                for ent in message.entities:
                    if ent.type == "bot_command" and message.text is not None:
                        command = message.text[ent.offset : ent.offset + ent.length]
                        break

            text_preview = None
            if not command and message.text:
                text_preview = (
                    message.text[:30] + "..."
                    if len(message.text) > 30
                    else message.text
                )

            logger.info(
                f"Incoming {event_type} | command={command} | user={user_name} (id={user_id})"
                + (f" | text={text_preview}" if text_preview else "")
            )

        return await handler(event, data)


middleware = LoggingMiddleware()
