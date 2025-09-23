# handlers/random.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.random_fact import get_random_fact_actions_keyboard
from utils.logger import get_logger
from services.openai_client import openai_client

from database.crud import update_user_stats
from database.models import User as DbUser
from lexicon.prompts import RANDOM_FACT_PROMPT
from callbacks.factories import RandomCallbackFactory

router = Router()
logger = get_logger(__name__)

priority = 50


@router.message(Command("random"))
async def command_random_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles the /random command.
    Sends a random fact to the user from ChatGPT.
    """
    await state.clear()

    status_message = await message.answer("⏳ Generating a random fact...")

    try:
        await update_user_stats(db, db_user, "random_facts_requested")
        response = await openai_client.get_response(RANDOM_FACT_PROMPT)
    except Exception as e:
        logger.error(f"Error generating random fact: {e}")
        response = "⚠️ An error occurred while generating a random fact."

    await status_message.edit_text(
        f"📜 {response}", reply_markup=get_random_fact_actions_keyboard()
    )


@router.callback_query(RandomCallbackFactory.filter(F.action == "get_fact"))
async def random_get_fact_callback(
    callback_query: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles the get_random_fact callback query.
    """
    await callback_query.answer()
    await command_random_handler(callback_query.message, state, db, db_user)
