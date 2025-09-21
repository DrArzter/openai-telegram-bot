# handlers/help.py
from aiogram import Router, html, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.help_menu import get_help_menu_keyboard
from utils.logger import get_logger

router = Router()
logger = get_logger(__name__)

HELP_TEXT = (
    "<b>🤖 ChatGPT Bot Help</b>\n\n"
    "🔹<b> Available commands:</b>\n"
    "/start - Start the bot and show main menu\n"
    "/help - Show this help message\n"
    "/random - Get a random fact\n"
    "/gpt - Ask ChatGPT directly\n"
    "\n"
    "💡 <b>How to use:</b>\n"
    "Use the menu buttons for easy navigation or type commands directly.\n\n"
    "🎯 <b>Features:</b>\n"
    "• Get random facts from ChatGPT\n"
    "• Ask any question directly\n"
)


@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    Handles the /help command.
    Sends a help message to the user.
    """

    await message.answer(HELP_TEXT, parse_mode="HTML")


@router.callback_query(F.data == "help")
async def help_handler(callback_query: CallbackQuery, state: FSMContext) -> None:

    await state.clear()
    await callback_query.answer()

    await callback_query.message.answer(
        HELP_TEXT,
        reply_markup=get_help_menu_keyboard(),
    )
