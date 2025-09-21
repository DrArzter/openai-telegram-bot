from aiogram import Router, html, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.logger import get_logger
from keyboards.start_menu import get_main_menu_keyboard

router = Router()
logger = get_logger(__name__)


@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """
    Handles the /start command.
    Sends a greeting message with the main menu keyboard.
    """

    user = message.from_user

    if user and user.username:
        welcome_text = (
            f"👋 Hello, {html.bold(user.username)}!\n\n"
            f"🤖 Welcome to the ChatGPT Bot.\n"
            f"💬 How can I help you today?\n"
            f"📚 Here you can ask questions and get answers from ChatGPT.\n"
            f"⬇️ Use the menu below to get started:"
        )
    else:
        welcome_text = (
            "👋 Hello!\n\n"
            "🤖 Welcome to the ChatGPT Bot.\n"
            "💬 How can I help you today?\n"
            "📚 Here you can ask questions and get answers from ChatGPT.\n"
            "⬇️ Use the menu below to get started:"
        )

    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())

    if user and user.username:
        logger.info(f"User {user.username} started the bot.")
    else:
        logger.info(f"Unknown user started the bot.")


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback_query: CallbackQuery, state: FSMContext) -> None:

    await state.clear()
    await callback_query.answer()

    await callback_query.message.answer(
        "👋 Welcome back to the ChatGPT Bot!\n\n"
        "💬 How can I help you today?\n"
        "📚 Here you can ask questions and get answers from ChatGPT.\n"
        "⬇️ Use the menu below to get started:",
        reply_markup=get_main_menu_keyboard(),
    )
