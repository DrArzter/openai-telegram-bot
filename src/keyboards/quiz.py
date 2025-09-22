# keyboards/quiz.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
    keyboard = [
        [
            InlineKeyboardButton(
                text=data["name"],
                callback_data=f"quiz_topic:{topic}",
            )
        ]
        for topic, data in QUIZ_TOPICS.items()
        if data["name"] and data["description"]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quiz_confirmation_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Choose another topic", callback_data="quiz:choose_topic"
            )
        ],
        [InlineKeyboardButton(text="✅ Start quiz", callback_data="quiz:continue")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="quiz:cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def qet_answer_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Choose another topic", callback_data="quiz:choose_topic"
            )
        ],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="quiz:cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_post_answer_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for post-quiz actions.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➡️ Continue", callback_data="quiz:continue"),
                InlineKeyboardButton(
                    text="🔄 Choose another topic", callback_data="quiz:choose_topic"
                ),
            ],
            [InlineKeyboardButton(text="🏠 To main menu", callback_data="quiz:cancel")],
        ]
    )
    return keyboard
