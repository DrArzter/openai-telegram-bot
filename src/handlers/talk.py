# handlers/talk.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.bot_states import PersonalityStates
from services.openai_client import openai_client
from keyboards.personality import (
    get_personality_selection_keyboard,
    get_personality_actions_keyboard,
)
from keyboards.start_menu import get_main_menu_keyboard
from utils.logger import get_logger

from database.crud import (
    save_conversation_message,
    get_conversation_history,
    update_user_stats,
)
from database.models import User as DbUser
from lexicon.prompts import PERSONALITY_PROMPTS, PERSONALITY_NAMES
from lexicon.messages import (
    TALK_MENU_TEXT,
    get_now_chatting_text,
    CHANGE_PERSONALITY_TEXT,
    END_CHAT_TEXT,
)
from callbacks.factories import PersonalityCallbackFactory

router = Router()
logger = get_logger(__name__)

priority = 50


@router.message(Command("talk"))
async def command_talk_handler(
    message: Message, state: FSMContext, db_user: DbUser
) -> None:
    """
    Handles the /talk command. Shows personality selection menu.
    """
    await state.clear()
    await state.set_state(PersonalityStates.choosing_personality)
    await message.answer(
        TALK_MENU_TEXT, reply_markup=get_personality_selection_keyboard()
    )
    logger.info(f"User {db_user.telegram_id} started personality talk")


@router.callback_query(PersonalityCallbackFactory.filter(F.action == "show_selection"))
async def talk_show_selection_callback(
    callback: CallbackQuery, state: FSMContext, db_user: DbUser
) -> None:
    """
    Handles callback to start personality selection.
    """
    await callback.answer()
    await command_talk_handler(callback.message, state, db_user)


@router.callback_query(PersonalityCallbackFactory.filter(F.action == "select"))
async def talk_select_personality_callback(
    callback: CallbackQuery,
    callback_data: PersonalityCallbackFactory,
    state: FSMContext,
    db: AsyncSession,
    db_user: DbUser,
) -> None:
    """
    Handles personality selection callback.
    """
    await callback.answer()
    personality_key = callback_data.key
    if not personality_key or personality_key not in PERSONALITY_PROMPTS:
        await callback.message.answer("❌ Unknown personality selected.")
        return

    # --- ИЗМЕНЕНИЕ: Обновляем статистику ---
    await update_user_stats(db, db_user, "personality_chats")

    await state.update_data(personality=personality_key)
    await state.set_state(PersonalityStates.chatting_with_personality)

    personality_name = PERSONALITY_NAMES[personality_key]
    text = get_now_chatting_text(personality_name)

    await callback.message.edit_text(
        text, reply_markup=get_personality_actions_keyboard()
    )
    logger.info(f"User {db_user.telegram_id} selected personality: {personality_key}")


@router.message(PersonalityStates.chatting_with_personality)
async def state_personality_chat_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles conversation with selected personality.
    """
    if not message.text:
        await message.answer("Please send a text message to continue the conversation.")
        return

    user_message = message.text
    state_data = await state.get_data()
    personality_key = state_data.get("personality")

    if not personality_key or personality_key not in PERSONALITY_PROMPTS:
        await message.answer(
            "❌ Personality not selected. Please start over with /talk"
        )
        await state.clear()
        return

    status_message = await message.answer("🤔 Thinking...")
    try:
        conversation_type = f"personality_{personality_key}"
        history_db = await get_conversation_history(db, db_user, conversation_type, 10)
        history_openai = [
            {"role": msg.role, "content": msg.content} for msg in history_db
        ]

        system_prompt = PERSONALITY_PROMPTS[personality_key]
        messages = [
            {"role": "system", "content": system_prompt},
            *history_openai,
            {"role": "user", "content": user_message},
        ]

        response = await openai_client.get_conversation_response(
            messages=messages, temperature=0.8
        )

        if response:
            await save_conversation_message(
                db, db_user, "user", user_message, conversation_type, personality_key
            )
            await save_conversation_message(
                db, db_user, "assistant", response, conversation_type, personality_key
            )

            personality_name = PERSONALITY_NAMES[personality_key]
            await status_message.edit_text(
                f"💬 <b>{personality_name}:</b>\n\n{response}",
                reply_markup=get_personality_actions_keyboard(),
            )
            logger.info(
                f"Personality {personality_key} responded to user {db_user.telegram_id}"
            )
        else:
            await status_message.edit_text(
                "❌ Sorry, I couldn't get a response.",
                reply_markup=get_personality_actions_keyboard(),
            )
    except Exception as e:
        logger.error(f"Error in personality chat for user {db_user.telegram_id}: {e}")
        await status_message.edit_text(
            "❌ An error occurred. Please try again.",
            reply_markup=get_personality_actions_keyboard(),
        )


@router.callback_query(PersonalityCallbackFactory.filter(F.action == "change"))
async def talk_change_personality_callback(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles callback to change personality.
    """
    await callback.answer()
    await state.set_state(PersonalityStates.choosing_personality)
    await callback.message.edit_text(
        CHANGE_PERSONALITY_TEXT,
        reply_markup=get_personality_selection_keyboard(),
    )


@router.callback_query(PersonalityCallbackFactory.filter(F.action == "end_chat"))
async def talk_end_chat_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to end personality chat.
    """
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        END_CHAT_TEXT,
        reply_markup=get_main_menu_keyboard(),
    )
