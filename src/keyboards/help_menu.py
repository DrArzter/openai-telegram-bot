# keyboards/help_menu.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_help_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🏠 Main menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
