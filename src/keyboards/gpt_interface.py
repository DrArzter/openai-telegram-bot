# keyboards/gpt_interface.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_gpt_interface_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown when starting GPT interface.
    """
    keyboard = [
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_gpt")],
        [InlineKeyboardButton(text="🏠 Main menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_gpt_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown after GPT response with action options.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="❓ Ask another question", callback_data="ask_another_gpt"
            )
        ],
        [InlineKeyboardButton(text="🏠 Main menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
