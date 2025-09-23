# handlers/quiz.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.start_menu import get_main_menu_keyboard
from states.bot_states import QuizStates
from services.openai_client import openai_client

from keyboards.quiz import (
    get_quiz_confirmation_keyboard,
    get_quiz_topic_selection_keyboard,
    get_post_answer_keyboard,
    get_answer_keyboard,
)
from utils.logger import get_logger

from database.crud import (
    clear_conversation_history,
    save_quiz_result,
    save_conversation_message,
    get_conversation_history,
    update_user_stats,
)
from database.models import User as DbUser
from lexicon.prompts import get_quiz_question_prompt, QUIZ_ANSWER_CHECK_PROMPT
from lexicon.topics import QUIZ_TOPICS
from callbacks.factories import QuizCallbackFactory

router = Router()
logger = get_logger(__name__)

priority = 50


@router.message(Command("quiz"))
async def command_quiz_handler(
    message: Message, state: FSMContext, db_user: DbUser
) -> None:
    await state.clear()
    await state.set_state(QuizStates.choosing_topic)
    await message.answer(
        "<b>Quiz time!</b>\n\n" "Please, choose a topic for the quiz:",
        reply_markup=get_quiz_topic_selection_keyboard(),
    )
    logger.info(f"User {db_user.telegram_id} started quiz")


@router.callback_query(QuizCallbackFactory.filter(F.action == "start"))
async def quiz_start_callback(
    callback: CallbackQuery, state: FSMContext, db_user: DbUser
) -> None:
    await callback.answer()
    await command_quiz_handler(callback.message, state, db_user)


@router.callback_query(QuizCallbackFactory.filter(F.action == "select_topic"))
async def quiz_select_topic_callback(
    callback: CallbackQuery,
    callback_data: QuizCallbackFactory,
    state: FSMContext,
    db: AsyncSession,
    db_user: DbUser,
) -> None:
    await callback.answer()
    await state.clear()
    await clear_conversation_history(db, db_user, "quiz")

    topic_key = callback_data.topic_key
    if not topic_key or topic_key not in QUIZ_TOPICS:
        await callback.message.answer("⚠️ Invalid topic selected.")
        return

    await state.update_data(topic=topic_key)
    await callback.message.answer(
        f"You have chosen the topic: {QUIZ_TOPICS[topic_key]['name']}\n\n"
        f"Are you ready to start the quiz?",
        reply_markup=get_quiz_confirmation_keyboard(),
    )


@router.callback_query(QuizCallbackFactory.filter(F.action == "choose_another_topic"))
async def quiz_reselect_topic_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    await callback.answer()
    data = await state.get_data()
    if data.get("total_questions", 0) > 0:
        await finish_quiz_session(db=db, user=db_user, state=state)

    await state.set_state(QuizStates.choosing_topic)
    await callback.message.answer(
        "Please choose another topic:", reply_markup=get_quiz_topic_selection_keyboard()
    )


@router.callback_query(QuizCallbackFactory.filter(F.action == "continue"))
async def quiz_continue_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    await callback.answer()
    data = await state.get_data()
    topic_key = data.get("topic")
    status_message = await callback.message.answer("🤔 Thinking...")

    if not topic_key:
        await status_message.edit_text(
            "⚠️ Topic not selected. Please choose a valid topic."
        )
        return

    try:
        history_db = await get_conversation_history(db, db_user, "quiz", 10)
        history_openai = [
            {"role": msg.role, "content": msg.content} for msg in history_db
        ]
        system_prompt = get_quiz_question_prompt(QUIZ_TOPICS[topic_key]["name"])
        messages = [{"role": "system", "content": system_prompt}, *history_openai]

        response = await openai_client.get_conversation_response(messages=messages)
        if response:
            await status_message.edit_text(response, reply_markup=get_answer_keyboard())
            await save_conversation_message(db, db_user, "assistant", response, "quiz")
            await state.set_state(QuizStates.waiting_for_answer)
    except Exception as e:
        logger.error(f"Error getting response from OpenAI: {e}")
        await status_message.edit_text(
            "⚠️ An error occurred while generating a question."
        )


@router.message(QuizStates.waiting_for_answer)
async def state_quiz_process_answer_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    if not message.text:
        await message.answer("Please provide a text answer.")
        return

    data = await state.get_data()
    if not data.get("topic"):
        await message.answer(
            "⚠️ Session expired. Please start a new quiz.",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
        return

    status_message = await message.answer("⏳ Processing your answer...")
    try:
        await save_conversation_message(db, db_user, "user", message.text, "quiz")
        history_db = await get_conversation_history(db, db_user, "quiz", 2)
        history_openai = [
            {"role": msg.role, "content": msg.content} for msg in history_db
        ]
        messages = [
            {"role": "system", "content": QUIZ_ANSWER_CHECK_PROMPT},
            *history_openai,
        ]

        response = await openai_client.get_conversation_response(messages=messages)
        if response:
            await save_conversation_message(db, db_user, "assistant", response, "quiz")
            is_correct = response.strip().lower() == "true"
            correct = data.get("correct_answers", 0) + (1 if is_correct else 0)
            total = data.get("total_questions", 0) + 1
            await state.update_data(correct_answers=correct, total_questions=total)
            result_text = f"{'✅ Correct!' if is_correct else '❌ Incorrect!'}\nSession progress: {correct}/{total} correct"
            await status_message.edit_text(result_text)
            await message.answer(
                "What would you like to do next?",
                reply_markup=get_post_answer_keyboard(),
            )
    except Exception as e:
        logger.error(f"Error processing quiz answer: {e}")
        await status_message.edit_text(
            "⚠️ An error occurred while processing your answer."
        )


@router.callback_query(QuizCallbackFactory.filter(F.action == "cancel"))
async def quiz_cancel_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    await callback.answer()
    await finish_quiz_session(db=db, user=db_user, state=state)
    await callback.message.answer(
        "❌ Quiz cancelled.\n\n👋 Welcome back to the main menu!",
        reply_markup=get_main_menu_keyboard(),
    )


async def finish_quiz_session(db: AsyncSession, user: DbUser, state: FSMContext):
    """
    Finishes the quiz session, saves the result, and clears the state.
    """
    data = await state.get_data()
    topic = data.get("topic")
    correct = data.get("correct_answers", 0)
    total = data.get("total_questions", 0)

    if topic and total > 0:
        await save_quiz_result(db, user, topic, correct, total)
        await update_user_stats(db, user, "quizzes_completed")

    await state.clear()
    await clear_conversation_history(db, user, "quiz")
