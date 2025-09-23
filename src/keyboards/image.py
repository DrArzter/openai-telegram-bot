# keyboards/image.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_image_interface_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_image")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)