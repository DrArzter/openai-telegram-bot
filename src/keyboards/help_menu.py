# keyboards/help_menu.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.factories import StartCallbackFactory


def get_help_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🏠 Main menu",
                callback_data=StartCallbackFactory(action="main_menu").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)