# keyboards/translate.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from callbacks.factories import TranslateCallbackFactory, StartCallbackFactory


def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🇩🇪 German",
                callback_data=TranslateCallbackFactory(
                    action="select_lang", language_code="de", language_name="German"
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🇯🇵 Japanese",
                callback_data=TranslateCallbackFactory(
                    action="select_lang", language_code="ja", language_name="Japanese"
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🇫🇷 French",
                callback_data=TranslateCallbackFactory(
                    action="select_lang", language_code="fr", language_name="French"
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏠 Main menu",
                callback_data=StartCallbackFactory(action="main_menu").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
