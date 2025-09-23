# keyboards/gpt_interface.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.factories import GPTCallbackFactory, StartCallbackFactory


def get_gpt_interface_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown when starting GPT interface.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data=GPTCallbackFactory(action="cancel").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Main menu",
                callback_data=StartCallbackFactory(action="main_menu").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_gpt_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown after GPT response with action options.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="❓ Ask another question",
                callback_data=GPTCallbackFactory(action="ask_another").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Main menu",
                callback_data=StartCallbackFactory(action="main_menu").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
