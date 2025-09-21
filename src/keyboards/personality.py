# keyboards/personality.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_personality_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard for selecting personalities.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="🧠 Einstein", callback_data="personality:einstein"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎭 Shakespeare", callback_data="personality:shakespeare"
            )
        ],
        [InlineKeyboardButton(text="💡 Steve Jobs", callback_data="personality:jobs")],
        [
            InlineKeyboardButton(
                text="🎨 Leonardo da Vinci", callback_data="personality:leonardo"
            )
        ],
        [InlineKeyboardButton(text="🏛️ Socrates", callback_data="personality:socrates")],
        [InlineKeyboardButton(text="🏠 Main menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_personality_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown during personality conversation.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔄 Change personality", callback_data="change_personality"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ End conversation", callback_data="end_personality_chat"
            )
        ],
        [InlineKeyboardButton(text="🏠 Main menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
