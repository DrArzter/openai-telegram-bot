# keyboards/image.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.factories import ImageCallbackFactory


def get_image_interface_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                # @router.callback_query(ImageCallbackFactory.filter(F.action == "cancel"))
                callback_data=ImageCallbackFactory(action="cancel").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)