# handlers/vocabulary.py
import random
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.bot_states import VocabularyStates
from services.openai_client import openai_client
from keyboards.vocabulary import get_vocabulary_actions_keyboard, get_practice_keyboard
from utils.logger import get_logger

from database.models import User as DbUser
from database.crud import (
    get_user_vocabulary,
    add_vocabulary_word,
    update_vocabulary_word_stats,
)
from callbacks.factories import VocabularyCallbackFactory
from lexicon.prompts import GET_NEW_WORD_PROMPT, get_word_validation_prompt
from lexicon.messages import (
    get_vocabulary_welcome_text,
    format_new_word_message,
    PRACTICE_START_TEXT,
    PRACTICE_NO_WORDS_TEXT,
    format_practice_word_prompt,
    format_practice_result_text,
)

router = Router()
logger = get_logger(__name__)
priority = 50


async def show_vocabulary_menu(
    message: Message | CallbackQuery,
    state: FSMContext,
    db: AsyncSession,
    db_user: DbUser,
):
    """Displays the main vocabulary menu and sets the learning_mode state."""
    await state.set_state(VocabularyStates.learning_mode)
    user_words = await get_user_vocabulary(db, db_user, "en")
    text = get_vocabulary_welcome_text(len(user_words))

    msg_to_edit_or_answer = message if isinstance(message, Message) else message.message

    if isinstance(message, CallbackQuery):
        await msg_to_edit_or_answer.edit_text(
            text, reply_markup=get_vocabulary_actions_keyboard()
        )
    else:
        await msg_to_edit_or_answer.answer(
            text, reply_markup=get_vocabulary_actions_keyboard()
        )


async def ask_next_practice_word(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
):
    """Asks the user the next word or finishes the practice session."""
    data = await state.get_data()
    words = data.get("practice_words", [])
    index = data.get("current_word_index", 0)

    if index < len(words):
        word_to_ask = words[index]
        await state.update_data(
            current_word_index=index + 1, current_word_id=word_to_ask["id"]
        )
        text = format_practice_word_prompt(word_to_ask["word"], index + 1, len(words))
        await message.answer(text)
        await state.set_state(VocabularyStates.waiting_for_translation)
    else:
        correct_answers = data.get("correct_answers", 0)
        total_questions = len(words)
        result_text = format_practice_result_text(correct_answers, total_questions)
        await message.answer(result_text)
        await show_vocabulary_menu(message, state, db, db_user)


@router.message(Command("vocabulary"))
async def command_vocabulary_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    await show_vocabulary_menu(message, state, db, db_user)


@router.callback_query(VocabularyCallbackFactory.filter(F.action == "start"))
async def vocabulary_start_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
):
    await callback.answer()
    await show_vocabulary_menu(callback, state, db, db_user)


@router.callback_query(
    VocabularyCallbackFactory.filter(F.action == "get_new_word"),
    VocabularyStates.learning_mode,
)
async def get_new_word_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
):
    await callback.answer()
    status_message = await callback.message.edit_text("🤔 Searching for a new word...")

    try:
        response = await openai_client.get_response(GET_NEW_WORD_PROMPT)
        if not response or response.count("|") != 2:
            await status_message.edit_text("Failed to get a word, please try again.")
            await show_vocabulary_menu(callback, state, db, db_user)
            return

        word, translation, example = map(str.strip, response.split("|"))
        await add_vocabulary_word(db, db_user, word, translation, "en")
        text = format_new_word_message(word, translation, example)
        await status_message.edit_text(
            text, reply_markup=get_vocabulary_actions_keyboard()
        )

    except Exception as e:
        logger.error(f"Error getting new word: {e}")
        await status_message.edit_text("An error occurred, please try again later.")


@router.callback_query(
    VocabularyCallbackFactory.filter(F.action == "start_practice"),
    VocabularyStates.learning_mode,
)
async def start_practice_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
):
    await callback.answer()
    await state.set_state(VocabularyStates.test_mode)
    words = await get_user_vocabulary(db, db_user, "en")

    if not words:
        await callback.message.edit_text(
            PRACTICE_NO_WORDS_TEXT, reply_markup=get_vocabulary_actions_keyboard()
        )
        await state.set_state(VocabularyStates.learning_mode)
        return

    await callback.message.edit_text(PRACTICE_START_TEXT)

    practice_words = [{"id": w.id, "word": w.word} for w in words]
    random.shuffle(practice_words)

    await state.update_data(
        practice_words=practice_words, current_word_index=0, correct_answers=0
    )
    await ask_next_practice_word(callback.message, state, db, db_user)


@router.message(VocabularyStates.waiting_for_translation)
async def practice_answer_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
):
    if not message.text:
        await message.answer("Please type the translation.")
        return

    user_answer = message.text
    data = await state.get_data()

    words = data.get("practice_words", [])
    index = data.get("current_word_index", 1) - 1
    current_word = words[index]

    status_message = await message.answer("⏳ Checking...")

    try:
        prompt = get_word_validation_prompt(current_word["word"], user_answer)
        response = await openai_client.get_response(prompt)
        is_correct = response.strip().lower() == "true"

        await update_vocabulary_word_stats(db, current_word["id"], is_correct)

        if is_correct:
            await status_message.edit_text("✅ Correct!")
            await state.update_data(correct_answers=data.get("correct_answers", 0) + 1)
        else:
            await status_message.edit_text("❌ Incorrect.")

        await state.set_state(VocabularyStates.test_mode)
        await ask_next_practice_word(message, state, db, db_user)

    except Exception as e:
        logger.error(f"Error validating word: {e}")
        await status_message.edit_text("An error occurred during validation.")
