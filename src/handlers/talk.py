# handlers/talk.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.bot_states import PersonalityStates
from services.openai_client import openai_client
from keyboards.personality import (
    get_personality_selection_keyboard,
    get_personality_actions_keyboard,
)
from utils.logger import get_logger
from utils.storage import save_conversation_message, get_conversation_history

router = Router()
logger = get_logger(__name__)

PERSONALITY_PROMPTS = {
    "einstein": "You are Albert Einstein. Respond as the famous physicist would, with curiosity about the universe, deep scientific insights, and philosophical reflections. Use his characteristic thoughtful and sometimes playful manner of speaking.",
    "shakespeare": "You are William Shakespeare. Respond in the eloquent, poetic style of the great playwright. Use rich metaphors, occasional Early Modern English phrases, and dramatic flair while discussing any topic.",
    "jobs": "You are Steve Jobs. Respond with passion for innovation, simplicity, and perfect design. Be direct, visionary, and sometimes challenging. Focus on thinking different and pushing boundaries.",
    "leonardo": "You are Leonardo da Vinci. Respond as the Renaissance genius would, with curiosity about everything - art, science, engineering, nature. Show your inventive spirit and artistic sensibility.",
    "socrates": "You are Socrates. Respond by asking probing questions to help people think deeper about their beliefs and assumptions. Use the Socratic method to guide conversations toward wisdom and self-knowledge.",
}

PERSONALITY_NAMES = {
    "einstein": "🧠 Albert Einstein",
    "shakespeare": "🎭 William Shakespeare",
    "jobs": "💡 Steve Jobs",
    "leonardo": "🎨 Leonardo da Vinci",
    "socrates": "🏛️ Socrates",
}


@router.message(Command("talk"))
async def command_talk_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the /talk command.
    Shows personality selection menu.
    """
    await state.clear()
    await state.set_state(PersonalityStates.choosing_personality)

    user_id = message.from_user.id if message.from_user else 0

    await message.answer(
        "💬 <b>Talk to Famous Personalities</b>\n\n"
        "Choose who you'd like to have a conversation with:\n\n"
        "🧠 <b>Einstein</b> - Discuss physics and universe\n"
        "🎭 <b>Shakespeare</b> - Explore literature and life\n"
        "💡 <b>Steve Jobs</b> - Talk innovation and design\n"
        "🎨 <b>Leonardo</b> - Renaissance art and science\n"
        "🏛️ <b>Socrates</b> - Philosophical discussions\n\n"
        "Select a personality below:",
        reply_markup=get_personality_selection_keyboard(),
    )

    logger.info(f"User {user_id} started personality talk")


@router.callback_query(F.data == "choose_personality")
async def choose_personality_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles callback to start personality selection.
    """
    await state.clear()
    await callback.answer()
    await state.set_state(PersonalityStates.choosing_personality)

    await callback.message.answer(
        "💬 <b>Talk to Famous Personalities</b>\n\n"
        "Choose who you'd like to have a conversation with:\n\n"
        "🧠 <b>Einstein</b> - Discuss physics and universe\n"
        "🎭 <b>Shakespeare</b> - Explore literature and life\n"
        "💡 <b>Steve Jobs</b> - Talk innovation and design\n"
        "🎨 <b>Leonardo</b> - Renaissance art and science\n"
        "🏛️ <b>Socrates</b> - Philosophical discussions\n\n"
        "Select a personality below:",
        reply_markup=get_personality_selection_keyboard(),
    )


@router.callback_query(F.data.startswith("personality:"))
async def select_personality_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles personality selection callback.
    """
    await callback.answer()

    personality_key = callback.data.split(":")[1]

    if personality_key not in PERSONALITY_PROMPTS:
        await callback.message.answer("❌ Unknown personality selected.")
        return

    await state.update_data(personality=personality_key)
    await state.set_state(PersonalityStates.chatting_with_personality)

    personality_name = PERSONALITY_NAMES[personality_key]
    user_id = callback.from_user.id if callback.from_user else 0

    await callback.message.answer(
        f"✨ <b>Now chatting with {personality_name}</b>\n\n"
        f"Start your conversation! Ask anything you'd like to discuss.\n\n"
        f"💭 Type your message below:",
        reply_markup=get_personality_actions_keyboard(),
    )

    logger.info(f"User {user_id} selected personality: {personality_key}")


@router.message(PersonalityStates.chatting_with_personality)
async def chat_with_personality(message: Message, state: FSMContext) -> None:
    """
    Handles conversation with selected personality.
    """
    if not message.text:
        await message.answer("Please send a text message to continue the conversation.")
        return

    user_id = message.from_user.id if message.from_user else 0
    user_message = message.text

    state_data = await state.get_data()
    personality_key = state_data.get("personality")

    if not personality_key or personality_key not in PERSONALITY_PROMPTS:
        await message.answer(
            "❌ Personality not selected. Please start over with /talk"
        )
        await state.clear()
        return

    personality_name = PERSONALITY_NAMES[personality_key]
    system_prompt = PERSONALITY_PROMPTS[personality_key]

    status_message = await message.answer("🤔 Thinking...")

    try:
        conversation_history = get_conversation_history(
            user_id=user_id,
            conversation_type=f"personality_{personality_key}",
            limit=10,
        )

        messages = []

        messages.append({"role": "system", "content": system_prompt})

        for hist_msg in conversation_history:
            messages.append({"role": hist_msg["role"], "content": hist_msg["content"]})

        messages.append({"role": "user", "content": user_message})

        response = await openai_client.get_conversation_response(
            messages=messages,
            temperature=0.8,
        )

        if response:
            save_conversation_message(
                user_id=user_id,
                role="user",
                content=user_message,
                conversation_type=f"personality_{personality_key}",
                persona=personality_key,
            )

            save_conversation_message(
                user_id=user_id,
                role="assistant",
                content=response,
                conversation_type=f"personality_{personality_key}",
                persona=personality_key,
            )

            await status_message.edit_text(
                f"💬 <b>{personality_name}:</b>\n\n{response}",
                reply_markup=get_personality_actions_keyboard(),
            )

            logger.info(f"Personality {personality_key} responded to user {user_id}")
        else:
            await status_message.edit_text(
                "❌ Sorry, I couldn't get a response. Please try again.",
                reply_markup=get_personality_actions_keyboard(),
            )

    except Exception as e:
        logger.error(f"Error in personality chat for user {user_id}: {e}")
        await status_message.edit_text(
            "❌ An error occurred. Please try again.",
            reply_markup=get_personality_actions_keyboard(),
        )


@router.callback_query(F.data == "change_personality")
async def change_personality_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles callback to change personality.
    """
    await callback.answer()
    await state.set_state(PersonalityStates.choosing_personality)

    await callback.message.answer(
        "💬 <b>Choose New Personality</b>\n\n" "Select who you'd like to talk with:",
        reply_markup=get_personality_selection_keyboard(),
    )


@router.callback_query(F.data == "end_personality_chat")
async def end_personality_chat_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles callback to end personality chat.
    """
    await state.clear()
    await callback.answer()

    from keyboards.start_menu import get_main_menu_keyboard

    await callback.message.answer(
        "👋 <b>Conversation Ended</b>\n\n"
        "Thank you for chatting! You can start a new conversation anytime.\n\n"
        "Welcome back to the main menu:",
        reply_markup=get_main_menu_keyboard(),
    )
