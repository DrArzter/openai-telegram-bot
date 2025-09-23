# handlers/gpt_interface.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.bot_states import GPTStates
from services.openai_client import openai_client
from keyboards.gpt_interface import get_gpt_interface_keyboard, get_gpt_actions_keyboard
from keyboards.start_menu import get_main_menu_keyboard
from utils.logger import get_logger

from database.crud import save_conversation_message, update_user_stats
from database.models import User as DbUser
from lexicon.prompts import GPT_SYSTEM_PROMPT
from callbacks.factories import GPTCallbackFactory

router = Router()
logger = get_logger(__name__)

priority = 50


@router.message(Command("gpt"))
async def command_gpt_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles the /gpt command.
    Sets FSM state to wait for user question.
    """
    await state.clear()
    await state.set_state(GPTStates.waiting_for_question)

    # --- ИЗМЕНЕНИЕ: Передаем объект db_user ---
    await update_user_stats(db, db_user, "gpt_queries")

    await message.answer(
        "🤖 <b>ChatGPT Interface</b>\n\n"
        "Ask me anything! I'll send your question directly to ChatGPT.\n\n"
        "💡 Examples:\n"
        "• Explain quantum physics simply\n"
        "• Write a poem about cats\n"
        "• Help me with Python code\n\n"
        "📝 Type your question below:",
        reply_markup=get_gpt_interface_keyboard(),
    )
    logger.info(f"User {db_user.telegram_id} started GPT interface")


@router.callback_query(GPTCallbackFactory.filter(F.action == "start"))
async def gpt_start_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles callback to start GPT interface.
    """
    await callback.answer()
    await command_gpt_handler(callback.message, state, db, db_user)


@router.message(GPTStates.waiting_for_question)
async def state_gpt_process_question_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Processes user's question and sends it to ChatGPT.
    """
    if not message.text:
        await message.answer(
            "❌ Please send a text question.\n"
            "Try again or use /start to return to main menu."
        )
        return

    user_question = message.text
    status_message = await message.answer("⏳ Processing your question...")

    try:
        await save_conversation_message(
            db=db,
            user=db_user,
            role="user",
            content=user_question,
            conversation_type="gpt_interface",
        )

        # --- ИЗМЕНЕНИЕ: Используем промпт из lexicon ---
        response = await openai_client.get_response(
            user_message=user_question,
            system_prompt=GPT_SYSTEM_PROMPT,
        )

        if response:
            await save_conversation_message(
                db=db,
                user=db_user,
                role="assistant",
                content=response,
                conversation_type="gpt_interface",
            )

            await status_message.edit_text(
                f"🤖 <b>ChatGPT Response:</b>\n\n{response}",
                reply_markup=get_gpt_actions_keyboard(),
            )
            await update_user_stats(db=db, user=db_user, stat_field="total_messages")
            logger.info(f"GPT response sent to user {db_user.telegram_id}")
        else:
            await status_message.edit_text(
                "❌ Sorry, I couldn't get a response from ChatGPT. Please try again.",
                reply_markup=get_gpt_actions_keyboard(),
            )
    except Exception as e:
        logger.error(
            f"Error processing GPT question for user {db_user.telegram_id}: {e}"
        )
        await status_message.edit_text(
            "❌ An error occurred while processing your question. Please try again.",
            reply_markup=get_gpt_actions_keyboard(),
        )
    finally:
        await state.set_state(GPTStates.waiting_for_question)


@router.callback_query(GPTCallbackFactory.filter(F.action == "ask_another"))
async def gpt_ask_another_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to ask another question to GPT.
    """
    await callback.answer()
    await state.set_state(GPTStates.waiting_for_question)

    await callback.message.answer(
        "🤖 <b>Ask Another Question</b>\n\n"
        "What would you like to know next?\n\n"
        "📝 Type your question below:",
        reply_markup=get_gpt_interface_keyboard(),
    )


@router.callback_query(GPTCallbackFactory.filter(F.action == "cancel"))
async def gpt_cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to cancel GPT interface.
    """
    await state.clear()
    await callback.answer()

    await callback.message.answer(
        "❌ ChatGPT session cancelled.\n\n" "👋 Welcome back to the main menu!",
        reply_markup=get_main_menu_keyboard(),
    )
