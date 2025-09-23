# keyboards/start_menu.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.factories import (
    RandomCallbackFactory,
    GPTCallbackFactory,
    PersonalityCallbackFactory,
    QuizCallbackFactory,
    ImageCallbackFactory,
    HelpCallbackFactory,
)


def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="📜 Get random fact",
                callback_data=RandomCallbackFactory(action="get_fact").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Ask ChatGPT",
                callback_data=GPTCallbackFactory(action="start").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Talk",
                callback_data=PersonalityCallbackFactory(
                    action="show_selection"
                ).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Quiz", callback_data=QuizCallbackFactory(action="start").pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="📸 Generate image caption",
                callback_data=ImageCallbackFactory(action="start").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ Help",
                callback_data=HelpCallbackFactory(action="show_menu").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
