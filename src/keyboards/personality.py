# keyboards/personality.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.prompts import PERSONALITY_NAMES
from callbacks.factories import PersonalityCallbackFactory, StartCallbackFactory


def get_personality_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for selecting personalities.
    """
    builder = InlineKeyboardBuilder()

    for key, name in PERSONALITY_NAMES.items():
        builder.row(
            InlineKeyboardButton(
                text=name,
                callback_data=PersonalityCallbackFactory(
                    action="select", key=key
                ).pack(),
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="🏠 Main menu",
            callback_data=StartCallbackFactory(action="main_menu").pack(),
        )
    )

    return builder.as_markup()


def get_personality_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown during personality conversation.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Change personality",
                callback_data=PersonalityCallbackFactory(action="change").pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ End conversation",
                callback_data=PersonalityCallbackFactory(action="end_chat").pack(),
            ),
            InlineKeyboardButton(
                text="🏠 Main menu",
                callback_data=StartCallbackFactory(action="main_menu").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
