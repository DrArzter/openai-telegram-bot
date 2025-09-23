# handlers/start.py
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from utils.logger import get_logger
from keyboards.start_menu import get_main_menu_keyboard

from database.models import User as DbUser
from lexicon.messages import get_welcome_message, MAIN_MENU_TEXT
from callbacks.factories import StartCallbackFactory

router = Router()
logger = get_logger(__name__)

priority = 50


@router.message(Command("start"))
async def command_start_handler(
    message: Message, state: FSMContext, db_user: DbUser
) -> None:
    """
    Handles the /start command.
    Sends a greeting message with the main menu keyboard.
    """
    await state.clear()

    welcome_text = get_welcome_message(db_user)

    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())

    logger.info(
        f"User {db_user.username or 'unknown'} (id={db_user.telegram_id}) started the bot."
    )


@router.callback_query(StartCallbackFactory.filter(F.action == "main_menu"))
async def start_main_menu_callback(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles the main_menu callback query.
    Returns the user to the main menu.
    """
    await state.clear()
    await callback_query.answer()

    await callback_query.message.edit_text(
        text=MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )
