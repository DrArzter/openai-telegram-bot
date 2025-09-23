# handlers/help.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.help_menu import get_help_menu_keyboard
from utils.logger import get_logger
from database.models import User as DbUser
from callbacks.factories import HelpCallbackFactory 

router = Router()
logger = get_logger(__name__)

priority = 50

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
async def command_help_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the /help command.
    Sends a help message to the user.
    """
    await state.clear()
    await message.answer(
        HELP_TEXT, parse_mode="HTML", reply_markup=get_help_menu_keyboard()
    )


@router.callback_query(HelpCallbackFactory.filter(F.action == "show_menu"))
async def help_menu_callback(
    callback_query: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles the help callback query.
    Sends a help message to the user.
    """
    await callback_query.answer()
    await command_help_handler(callback_query.message, state)