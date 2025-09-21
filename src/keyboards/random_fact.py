# keyboards/random_fact.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_random_fact_actions_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🎲 Another fact", callback_data="get_random_fact")],
        [InlineKeyboardButton(text="🏠 Main menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
