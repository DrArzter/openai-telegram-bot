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
    return (
        f"✨ <b>Now chatting with {personality_name}</b>\n\n"
        f"Start your conversation! Ask anything you'd like to discuss.\n\n"
        f"💭 Type your message below:"
    )


CHANGE_PERSONALITY_TEXT = (
    "💬 <b>Choose New Personality</b>\n\nSelect who you'd like to talk with:"
)
END_CHAT_TEXT = (
    "👋 <b>Conversation Ended</b>\n\n"
    "Thank you for chatting! You can start a new conversation anytime.\n\n"
    "Welcome back to the main menu:"
)

IMAGE_REC_START_TEXT = "Send me an image, and I will tell you what's on it."

CHOOSE_LANGUAGE_TEXT = "Please choose the language you want to translate to:"
WAITING_FOR_TEXT_TEXT = "Now, send me the text you want to translate."


def get_translation_result_text(original: str, translation: str, language: str) -> str:
    return (
        f"🌍 <b>Translation to {language}</b>\n\n"
        f"<b>Original:</b>\n<code>{html.quote(original)}</code>\n\n"
        f"<b>Translation:</b>\n<code>{html.quote(translation)}</code>"
    )


def get_vocabulary_welcome_text(words_count: int) -> str:
    return (
        f"📚 **Vocabulary Trainer**\n\n"
        f"You have learned {words_count} words.\n\n"
        "Press 'New word' to learn another one, or 'Practice' to test your knowledge."
    )


def format_new_word_message(word: str, translation: str, example: str) -> str:
    return (
        f"✨ **New word:**\n\n"
        f"🇬🇧 **{word.capitalize()}** — 🇷🇺 {translation.capitalize()}\n\n"
        f"<i>Example: {example}</i>"
    )


PRACTICE_START_TEXT = "💪 **Practice session has started!**\n\nI will send you words, and you will provide their translation."
PRACTICE_NO_WORDS_TEXT = "You haven't learned any words yet. Press 'New word' to start!"


def format_practice_word_prompt(word: str, current: int, total: int) -> str:
    return f"**Word {current}/{total}:**\n\nWhat is the translation of ` {word} `?"


def format_practice_result_text(correct: int, total: int) -> str:
    percentage = int((correct / total) * 100) if total > 0 else 0
    return (
        f"🎉 **Practice finished!**\n\n"
        f"Your result: {correct} out of {total} ({percentage}%)\n\n"
        "Great job! Would you like to practice again?"
    )
