# keyboards/quiz.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.factories import QuizCallbackFactory

QUIZ_TOPICS = {
    "science": {
        "name": "🔬 Science & Nature",
        "description": "Physics, chemistry, biology, astronomy",
    },
    "history": {
        "name": "📚 History",
        "description": "World history, famous events and personalities",
    },
    "geography": {
        "name": "🌍 Geography",
        "description": "Countries, capitals, landmarks, nature",
    },
    "technology": {
        "name": "💻 Technology",
        "description": "IT, programming, gadgets, innovations",
    },
    "arts": {
        "name": "🎨 Arts & Culture",
        "description": "Literature, music, movies, painting",
    },
    "sports": {
        "name": "⚽ Sports",
        "description": "Various sports, athletes, championships",
    },
    "general": {
        "name": "🧠 General Knowledge",
        "description": "Mixed topics, trivia, common facts",
    },
}


def get_quiz_topic_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for selecting topics in the quiz.
    """
    builder = InlineKeyboardBuilder()
    for topic_key, data in QUIZ_TOPICS.items():
        builder.row(
            InlineKeyboardButton(
                text=data["name"],
                callback_data=QuizCallbackFactory(
                    action="select_topic", topic_key=topic_key
                ).pack(),
            )
        )
    return builder.as_markup()


def get_quiz_confirmation_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Choose another topic",
                callback_data=QuizCallbackFactory(action="choose_another_topic").pack(),
            ),
            InlineKeyboardButton(
                text="✅ Start quiz",
                callback_data=QuizCallbackFactory(action="continue").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data=QuizCallbackFactory(action="cancel").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_answer_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Choose another topic",
                callback_data=QuizCallbackFactory(action="choose_another_topic").pack(),
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data=QuizCallbackFactory(action="cancel").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_post_answer_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for post-quiz actions.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="➡️ Continue",
                callback_data=QuizCallbackFactory(action="continue").pack(),
            ),
            InlineKeyboardButton(
                text="🔄 Choose another topic",
                callback_data=QuizCallbackFactory(action="choose_another_topic").pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="🏠 To main menu",
                callback_data=QuizCallbackFactory(action="cancel").pack(),
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
