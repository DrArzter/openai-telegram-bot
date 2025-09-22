# handlers/random.py
from aiogram import Router, html, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.random_fact import get_random_fact_actions_keyboard
from utils.logger import get_logger
from services.openai_client import openai_client

router = Router()
logger = get_logger(__name__)

RANDOM_FACT_PROMPT = (
    "Tell me a random, interesting, short fact that hasn't been said before."
)


@router.message(Command("random"))
async def command_random_handler(message: Message) -> None:
    """
    Handles the /random command.
    Sends a random fact to the user from ChatGPT.
    """

    status_message = await message.answer("⏳ Generating a random fact...")

    try:
        response = await openai_client.get_response(RANDOM_FACT_PROMPT)
    except Exception as e:
        logger.error(f"Error generating random fact: {e}")
        response = "⚠️ An error occurred while generating a random fact."
    await status_message.edit_text(
        f"📜 {response}", reply_markup=get_random_fact_actions_keyboard()
    )


@router.callback_query(F.data == "get_random_fact")
async def get_random_fact_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles the get_random_fact callback query.
    """

    await state.clear()
    await callback_query.answer()

    status_message = await callback_query.message.answer(
        "⏳ Generating a random fact..."
    )

    try:
        response = await openai_client.get_response(RANDOM_FACT_PROMPT)
    except Exception as e:
        logger.error(f"Error generating random fact: {e}")
        response = "⚠️ An error occurred while generating a random fact."
    await status_message.edit_text(
        f"📜 {response}", reply_markup=get_random_fact_actions_keyboard()
    )
