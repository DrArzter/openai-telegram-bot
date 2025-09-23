# lexicon/messages.py
from aiogram import html
from database.models import User as DbUser

def get_welcome_message(user: DbUser | None) -> str:
    """Generates a personalized welcome message."""
    if user and user.username is not None:
        text = (
            f"👋 Hello, {user.username}!\n\n"
            f"🤖 Welcome to the ChatGPT Bot.\n"
            f"💬 How can I help you today?\n"
            f"📚 Here you can ask questions and get answers from ChatGPT.\n"
            f"⬇️ Use the menu below to get started:"
        )
    else:
        text = (
            "👋 Hello!\n\n"
            "🤖 Welcome to the ChatGPT Bot.\n"
            "💬 How can I help you today?\n"
            "📚 Here you can ask questions and get answers from ChatGPT.\n"
            "⬇️ Use the menu below to get started:"
        )
    return text

MAIN_MENU_TEXT = (
    "👋 Welcome back to the ChatGPT Bot!\n\n"
    "💬 How can I help you today?\n"
    "📚 Here you can ask questions and get answers from ChatGPT.\n"
    "⬇️ Use the menu below to get started:"
)

# --- Talk Handler Texts ---
TALK_MENU_TEXT = (
    "💬 <b>Talk to Famous Personalities</b>\n\n"
    "Choose who you'd like to have a conversation with:\n\n"
    "🧠 <b>Einstein</b> - Discuss physics and universe\n"
    "🎭 <b>Shakespeare</b> - Explore literature and life\n"
    "💡 <b>Steve Jobs</b> - Talk innovation and design\n"
    "🎨 <b>Leonardo</b> - Renaissance art and science\n"
    "🏛️ <b>Socrates</b> - Philosophical discussions\n\n"
    "Select a personality below:"
)

def get_now_chatting_text(personality_name: str) -> str:
    """Generates the text for starting a chat with a personality."""
    return (
        f"✨ <b>Now chatting with {personality_name}</b>\n\n"
        f"Start your conversation! Ask anything you'd like to discuss.\n\n"
        f"💭 Type your message below:"
    )

CHANGE_PERSONALITY_TEXT = "💬 <b>Choose New Personality</b>\n\nSelect who you'd like to talk with:"

END_CHAT_TEXT = (
    "👋 <b>Conversation Ended</b>\n\n"
    "Thank you for chatting! You can start a new conversation anytime.\n\n"
    "Welcome back to the main menu:"
)