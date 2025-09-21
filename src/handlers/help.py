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
    "<b>ChatGPT Bot Help</b>\n\n"
    "🔹 <b> Available commands:</b>\n"
    "/start - Start the bot and show main menu\n"
    "/help - Show this help message\n"
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
