# keyboards/start_menu.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📜 Get random fact", callback_data="get_random_fact")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
