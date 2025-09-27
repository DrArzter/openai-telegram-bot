# keyboards/vocabulary.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.factories import VocabularyCallbackFactory, StartCallbackFactory


def get_vocabulary_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for main actions in the vocabulary trainer.
    "Ещё слово", "Тренироваться", и "Закончить".
    """

    keyboard = [
        [
            InlineKeyboardButton(
                text="🆕 New word",
                callback_data=VocabularyCallbackFactory(action="get_new_word").pack(),
            ),
            InlineKeyboardButton(
                text="🎯 Practice",
                callback_data=VocabularyCallbackFactory(action="start_practice").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏁 Finish",
                callback_data=StartCallbackFactory(action="main_menu").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_practice_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown during a practice session, allowing to end it prematurely.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="🏁 End Practice",
                callback_data=VocabularyCallbackFactory(action="start").pack(),
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
