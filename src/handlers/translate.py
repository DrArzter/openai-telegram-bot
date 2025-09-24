# handlers/translate.py
from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.translate import get_language_keyboard
from states.bot_states import TranslatorStates
from services.openai_client import openai_client
from utils.logger import get_logger

from database.models import User as DbUser
from database.crud import save_translation, update_user_stats
from callbacks.factories import TranslateCallbackFactory, StartCallbackFactory
from lexicon.prompts import get_translation_prompt
from lexicon.messages import (
    CHOOSE_LANGUAGE_TEXT,
    WAITING_FOR_TEXT_TEXT,
    get_translation_result_text,
)

router = Router()
logger = get_logger(__name__)

priority = 50


@router.message(Command("translate"))
async def command_translate_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the /translate command.
    """
    await state.clear()
    await state.set_state(TranslatorStates.choosing_language)
    await message.answer(CHOOSE_LANGUAGE_TEXT, reply_markup=get_language_keyboard())


@router.callback_query(TranslateCallbackFactory.filter(F.action == "start"))
async def translate_start_callback(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    """
    Handles the callback from the main menu to start translation.
    """
    await state.clear()
    await callback_query.answer()
    await state.set_state(TranslatorStates.choosing_language)
    await callback_query.message.edit_text(
        CHOOSE_LANGUAGE_TEXT, reply_markup=get_language_keyboard()
    )


@router.callback_query(TranslateCallbackFactory.filter(F.action == "select_lang"))
async def select_language_callback(
    callback_query: CallbackQuery,
    callback_data: TranslateCallbackFactory,
    state: FSMContext,
) -> None:
    """
    Handles language selection and sets state to wait for text.
    """
    await callback_query.answer()

    language_code = callback_data.language_code
    language_name = callback_data.language_name

    await state.update_data(
        target_language_code=language_code,
        target_language_name=language_name,
    )
    await state.set_state(TranslatorStates.waiting_for_text)
    await callback_query.message.edit_text(WAITING_FOR_TEXT_TEXT)


@router.message(TranslatorStates.waiting_for_text)
async def process_translation_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Receives text, translates it, saves to DB, and shows result.
    """
    if not message.text:
        await message.answer("Please send me some text to translate.")
        return

    data = await state.get_data()
    target_lang_name = data.get("target_language_name")

    if not target_lang_name:
        await message.answer(
            "Language not selected. Please start over with /translate."
        )
        await state.clear()
        return

    original_text = message.text
    status_message = await message.answer(f"⏳ Translating to {target_lang_name}...")

    try:
        prompt = get_translation_prompt(original_text, target_lang_name)
        translated_text = await openai_client.get_response(prompt)

        if not translated_text:
            await status_message.edit_text("Sorry, I couldn't translate this text.")
            return

        await save_translation(
            db=db,
            user=db_user,
            original_text=original_text,
            translated_text=translated_text,
            target_language=target_lang_name,
        )

        result_text = get_translation_result_text(
            original_text, translated_text, target_lang_name
        )
        await status_message.edit_text(
            result_text, reply_markup=get_language_keyboard()
        )

        await state.set_state(TranslatorStates.choosing_language)

    except Exception as e:
        logger.error(f"Error during translation for user {db_user.telegram_id}: {e}")
        await status_message.edit_text("An error occurred during translation.")
        await state.clear()
