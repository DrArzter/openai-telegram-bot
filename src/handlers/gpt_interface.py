# handlers/gpt_interface.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.bot_states import GPTStates
from services.openai_client import openai_client
from keyboards.gpt_interface import get_gpt_interface_keyboard, get_gpt_actions_keyboard
from utils.logger import get_logger
from utils.storage import save_conversation_message, update_user_stats

router = Router()
logger = get_logger(__name__)


@router.message(Command("gpt"))
async def command_gpt_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the /gpt command.
    Sets FSM state to wait for user question.
    """
    user_id = message.from_user.id if message.from_user else 0

    await state.clear()

    await state.set_state(GPTStates.waiting_for_question)

    update_user_stats(user_id, "gpt_queries")

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

    logger.info(f"User {user_id} started GPT interface")


@router.callback_query(F.data == "start_gpt")
async def start_gpt_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to start GPT interface.
    """
    await state.clear()
    await callback.answer()

    user_id = callback.from_user.id if callback.from_user else 0

    await state.set_state(GPTStates.waiting_for_question)

    update_user_stats(user_id, "gpt_queries")

    await callback.message.answer(
        "🤖 <b>ChatGPT Interface</b>\n\n"
        "Ask me anything! I'll send your question directly to ChatGPT.\n\n"
        "💡 Examples:\n"
        "• Explain quantum physics simply\n"
        "• Write a poem about cats\n"
        "• Help me with Python code\n\n"
        "📝 Type your question below:",
        reply_markup=get_gpt_interface_keyboard(),
    )


@router.message(GPTStates.waiting_for_question)
async def process_gpt_question(message: Message, state: FSMContext) -> None:
    """
    Processes user's question and sends it to ChatGPT.
    """
    if not message.text:
        await message.answer(
            "❌ Please send a text question.\n"
            "Try again or use /start to return to main menu."
        )
        return

    user_id = message.from_user.id if message.from_user else 0
    user_question = message.text

    status_message = await message.answer("⏳ Processing your question...")

    try:
        save_conversation_message(
            user_id=user_id,
            role="user",
            content=user_question,
            conversation_type="gpt_interface",
        )

        response = await openai_client.get_response(
            user_message=user_question,
            system_prompt="You are a helpful AI assistant. Provide clear, accurate, and helpful responses.",
        )

        if response:
            save_conversation_message(
                user_id=user_id,
                role="assistant",
                content=response,
                conversation_type="gpt_interface",
            )

            await status_message.edit_text(
                f"🤖 <b>ChatGPT Response:</b>\n\n{response}",
                reply_markup=get_gpt_actions_keyboard(),
            )

            update_user_stats(user_id, "total_messages")

            logger.info(f"GPT response sent to user {user_id}")
        else:
            await status_message.edit_text(
                "❌ Sorry, I couldn't get a response from ChatGPT. Please try again.",
                reply_markup=get_gpt_actions_keyboard(),
            )

    except Exception as e:
        logger.error(f"Error processing GPT question for user {user_id}: {e}")
        await status_message.edit_text(
            "❌ An error occurred while processing your question. Please try again.",
            reply_markup=get_gpt_actions_keyboard(),
        )

    await state.clear()


@router.callback_query(F.data == "ask_another_gpt")
async def ask_another_gpt_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to ask another question to GPT.
    """
    await state.clear()
    await callback.answer()

    await state.set_state(GPTStates.waiting_for_question)

    await callback.message.answer(
        "🤖 <b>Ask Another Question</b>\n\n"
        "What would you like to know next?\n\n"
        "📝 Type your question below:",
        reply_markup=get_gpt_interface_keyboard(),
    )


@router.callback_query(F.data == "cancel_gpt")
async def cancel_gpt_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to cancel GPT interface.
    """
    await state.clear()
    await callback.answer()

    from keyboards.start_menu import get_main_menu_keyboard

    await callback.message.answer(
        "❌ ChatGPT session cancelled.\n\n" "👋 Welcome back to the main menu!",
        reply_markup=get_main_menu_keyboard(),
    )
