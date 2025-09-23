# keyboards/random_fact.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.factories import RandomCallbackFactory, StartCallbackFactory


def get_random_fact_actions_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🎲 Another fact",
                callback_data=RandomCallbackFactory(action="get_fact").pack(),
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
