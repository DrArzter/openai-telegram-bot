# middlewares/logging.py
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_name = "unknown"
        user_id = "unknown"
        command = None
        text_preview = None
        callback_data = None

        event_type = type(event).__name__

        if isinstance(event, Message):
            user = event.from_user
            user_name = user.username if user and user.username else "unknown"
            user_id = user.id if user else "unknown"

            if event.entities:
                for ent in event.entities:
                    if ent.type == "bot_command" and event.text is not None:
                        command = event.text[ent.offset : ent.offset + ent.length]
                        break

            if not command and event.text:
                text_preview = (
                    event.text[:30] + "..." if len(event.text) > 30 else event.text
                )

        elif isinstance(event, CallbackQuery):
            user = event.from_user
            user_name = user.username if user and user.username else "unknown"
            user_id = user.id if user else "unknown"
            callback_data = event.data

        else:
            if hasattr(event, "callback_query") and event.callback_query:
                callback_event = event.callback_query
                user = callback_event.from_user
                user_name = user.username if user and user.username else "unknown"
                user_id = user.id if user else "unknown"
                callback_data = callback_event.data
                event_type = "CallbackQuery"

            elif hasattr(event, "message") and event.message:
                message_event = event.message
                user = message_event.from_user
                user_name = user.username if user and user.username else "unknown"
                user_id = user.id if user else "unknown"
                event_type = "Message"

                if message_event.entities:
                    for ent in message_event.entities:
                        if ent.type == "bot_command" and message_event.text is not None:
                            command = message_event.text[
                                ent.offset : ent.offset + ent.length
                            ]
                            break

                if not command and message_event.text:
                    text_preview = (
                        message_event.text[:30] + "..."
                        if len(message_event.text) > 30
                        else message_event.text
                    )

        log_parts = [f"Incoming {event_type}"]

        if command:
            log_parts.append(f"command={command}")
        elif callback_data:
            log_parts.append(f"callback={callback_data}")
        elif text_preview:
            log_parts.append(f"text={text_preview}")

        log_parts.append(f"user={user_name} (id={user_id})")

        logger.info(" | ".join(log_parts))

        return await handler(event, data)


middleware = LoggingMiddleware()
