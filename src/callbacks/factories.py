# callbacks/factories.py
from aiogram.filters.callback_data import CallbackData


class StartCallbackFactory(CallbackData, prefix="start"):
    action: str


class TranslateCallbackFactory(CallbackData, prefix="translate"):
    action: str
    language_code: str | None = None
    language_name: str | None = None


class GPTCallbackFactory(CallbackData, prefix="gpt"):
    action: str


class HelpCallbackFactory(CallbackData, prefix="help"):
    action: str


class ImageCallbackFactory(CallbackData, prefix="image"):
    action: str


class PersonalityCallbackFactory(CallbackData, prefix="personality"):
    action: str
    key: str | None = None


class QuizCallbackFactory(CallbackData, prefix="quiz"):
    action: str
    topic_key: str | None = None


class RandomCallbackFactory(CallbackData, prefix="random"):
    action: str
