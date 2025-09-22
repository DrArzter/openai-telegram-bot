# handlers/quiz.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.start_menu import get_main_menu_keyboard
from states.bot_states import QuizStates
from services.openai_client import openai_client

from keyboards.quiz import (
    get_quiz_confirmation_keyboard,
    get_quiz_topic_selection_keyboard,
    get_post_answer_keyboard,
    QUIZ_TOPICS,
    qet_answer_keyboard,
)
from utils.logger import get_logger
from utils.storage import (
    clear_conversation_history,
    save_quiz_result,
    save_conversation_message,
    get_conversation_history,
)

router = Router()
logger = get_logger(__name__)


@router.message(Command("quiz"))
async def command_quiz_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the /quiz command.
    """

    await state.clear()
    await state.set_state(QuizStates.choosing_topic)

    user_id = message.from_user.id if message.from_user else 0

    await message.answer(
        "<b>Quiz time!</b>\n\n" "Please, choose a topic for the quiz:",
        reply_markup=get_quiz_topic_selection_keyboard(),
    )

    logger.info(f"User {user_id} started quiz")


@router.callback_query(F.data == "quiz")
async def quiz_start_callback(callback: CallbackQuery, state: FSMContext) -> None:

    await callback.answer()
    await state.clear()

    await command_quiz_handler(callback.message, state)


@router.callback_query(F.data.startswith("quiz_topic:"))
async def select_topic_callback(callback: CallbackQuery, state: FSMContext) -> None:

    await callback.answer()
    await state.clear()

    user_id = callback.from_user.id if callback.from_user else 0

    clear_conversation_history(user_id=user_id, conversation_type="quiz")

    topic_key = callback.data.split(":")[1]

    if topic_key not in QUIZ_TOPICS:
        await callback.message.answer(
            "⚠️ Invalid topic selected. Please choose a valid topic.",
            reply_markup=get_quiz_topic_selection_keyboard(),
        )
        return

    await state.update_data(topic=topic_key)

    await callback.message.answer(
        f"You have chosen the topic: {QUIZ_TOPICS[topic_key]['name']}\n\n"
        f"Are you ready to start the quiz? Click the button below to continue:",
        reply_markup=get_quiz_confirmation_keyboard(),
    )


@router.callback_query(F.data == "quiz:choose_topic")
async def reselect_topic_callback(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    data = await state.get_data()

    if data.get("total_questions", 0) > 0:
        await finish_quiz_session(user_id=user_id, state=state)

    await state.set_state(QuizStates.choosing_topic)

    await callback.message.answer(
        "Please choose another topic:",
        reply_markup=get_quiz_topic_selection_keyboard(),
    )


@router.callback_query(F.data == "quiz:continue")
async def continue_quiz(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Continues the quiz and prepares the next question.
    """

    await callback.answer()

    data = await state.get_data()
    topic = data.get("topic")

    status_message = await callback.message.answer("🤔 Thinking...")

    if not topic:
        logger.error("For some reason topic is not set in continue_quiz callback")
        await callback.message.answer(
            "⚠️ Invalid topic selected. Please choose a valid topic.",
            reply_markup=get_quiz_topic_selection_keyboard(),
        )
        return

    user_id = callback.from_user.id if callback.from_user else 0

    try:
        conversation_history = get_conversation_history(
            user_id=user_id,
            conversation_type=f"quiz",
            limit=10,
        )

        messages = []

        messages.append(
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant."
                    "You have to play a quiz with the user."
                    f"Your task is to give user a quiz question on topic: {topic}."
                    "Try not to ask the same question for the same topic."
                    "Do not ask if you should ask another question."
                ),
            }
        )
        for message in conversation_history:
            messages.append({"role": message["role"], "content": message["content"]})

        response = await openai_client.get_conversation_response(
            messages=messages,
        )

        if response:
            await status_message.edit_text(response, reply_markup=qet_answer_keyboard())
            save_conversation_message(
                user_id=user_id,
                conversation_type=f"quiz",
                role="assistant",
                content=response,
            )

            await state.set_state(QuizStates.waiting_for_answer)

    except Exception as e:
        logger.error(f"Error while getting response from OpenAI: {e}")


@router.message(QuizStates.waiting_for_answer)
async def process_quiz_answer(message: Message, state: FSMContext) -> None:

    data = await state.get_data()
    topic = data.get("topic")

    if not topic:
        logger.error("Topic not set in process_quiz_answer")
        await message.answer(
            "⚠️ Invalid topic selected. Please choose a valid topic.",
            reply_markup=get_quiz_topic_selection_keyboard(),
        )
        return

    user_id = message.from_user.id if message.from_user else 0

    logger.info(f"User {user_id} submitted answer: {message.text}")

    status_message = await message.answer("⏳ Processing your answer...")

    try:
        save_conversation_message(
            user_id=user_id,
            role="user",
            content=message.text,
            conversation_type="quiz",
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict quiz assistant. "
                    "You have already asked the user a quiz question. "
                    "User has just submitted an answer. "
                    "ONLY respond with True if the answer is correct, or False if it is incorrect. "
                    "Do NOT provide any explanations, reasoning, or extra text. "
                    "ONLY True or False."
                ),
            }
        ]

        conversation_history = get_conversation_history(
            user_id=user_id, conversation_type="quiz", limit=2
        )

        for hist_msg in conversation_history:
            messages.append({"role": hist_msg["role"], "content": hist_msg["content"]})

        response = await openai_client.get_conversation_response(messages=messages)

        if response:
            save_conversation_message(
                user_id=user_id,
                conversation_type="quiz",
                role="assistant",
                content=response,
            )

            status = response.strip().lower() == "true"

            correct_answers = data.get("correct_answers", 0)
            total_questions = data.get("total_questions", 0)

            correct_answers += 1 if status else 0
            total_questions += 1

            await state.update_data(
                correct_answers=correct_answers, total_questions=total_questions
            )

            result_text = (
                f"{'✅ Correct!' if status else '❌ Incorrect!'}\n"
                f"Session progress: {correct_answers}/{total_questions} correct"
            )

            await status_message.edit_text(result_text)
            await message.answer(
                "What would you like to do next?",
                reply_markup=get_post_answer_keyboard(),
            )

    except Exception as e:
        logger.error(f"Error while processing quiz answer: {e}")
        await message.answer("⚠️ An error occurred while processing your answer.")


@router.callback_query(F.data == "quiz:cancel")
async def cancel_quiz_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles callback to cancel quiz.
    """
    await callback.answer()
    user_id = callback.from_user.id if callback.from_user else 0

    await finish_quiz_session(user_id=user_id, state=state)

    await callback.message.answer(
        "❌ Quiz cancelled.\n\n👋 Welcome back to the main menu!",
        reply_markup=get_main_menu_keyboard(),
    )


async def finish_quiz_session(user_id: int, state: FSMContext):
    """
    Handles q

    Args:
        user_id (int): user id
        state (FSMContext): FSM context
    """
    data = await state.get_data()
    topic = data.get("topic")
    correct_answers = data.get("correct_answers", 0)
    total_questions = data.get("total_questions", 0)

    if topic and total_questions > 0:
        save_quiz_result(
            user_id=user_id,
            topic=topic,
            correct_answers=correct_answers,
            total_questions=total_questions,
        )

    await state.clear()
    clear_conversation_history(user_id=user_id, conversation_type="quiz")
