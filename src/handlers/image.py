# handlers/image.py
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.image import get_image_interface_keyboard
from states.bot_states import VisionStates
from services.openai_client import openai_client

from database.models import User as DbUser
from database.crud import update_user_stats
from lexicon.prompts import IMAGE_DESCRIPTION_PROMPT
from utils.logger import get_logger
from callbacks.factories import ImageCallbackFactory

logger = get_logger(__name__)
router = Router()

priority = 50


@router.message(Command("image"))
async def command_image_handler(
    message: Message, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles the /image command.
    Clears the current state and sets it to waiting for an image.
    Sends a message to the user asking them to send an image.
    """
    await state.clear()
    await state.set_state(VisionStates.waiting_for_image)

    await update_user_stats(db, db_user, "image_descriptions_generated")

    await message.answer(
        "Send me an image and I'll generate a description for it!",
        reply_markup=get_image_interface_keyboard(),
    )


@router.callback_query(ImageCallbackFactory.filter(F.action == "start"))
async def image_start_callback(
    callback: CallbackQuery, state: FSMContext, db: AsyncSession, db_user: DbUser
) -> None:
    """
    Handles the image callback query.
    Clears the current state and sets it to waiting for an image.
    Sends a message to the user asking them to send an image.
    """
    await callback.answer()
    await command_image_handler(callback.message, state, db, db_user)


@router.message(VisionStates.waiting_for_image, F.photo | F.document)
async def state_vision_process_image_handler(
    message: Message, state: FSMContext, bot: Bot
) -> None:
    """
    Handles the image message.
    Downloads the image and generates a caption for it using the OpenAI API.
    Sends the caption back to the user and clears the current state.
    """
    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        if "image" in (message.document.mime_type or ""):
            file_id = message.document.file_id
        else:
            await message.answer(
                "Only images are supported. Please send an image. (jpg, png, etc.)"
            )
            return

    if not file_id:
        await message.answer("Could not process the image.")
        return

    status_message = await message.answer("⏳ Processing image...")

    try:
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        image_bytes = downloaded_file.read()

        caption = await openai_client.describe_image(
            image_bytes=image_bytes, prompt=IMAGE_DESCRIPTION_PROMPT
        )

        await status_message.edit_text(
            caption or "Unfortunately, I could not generate a caption for this image."
        )

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await status_message.edit_text("An error occurred while processing the image.")
    finally:
        await state.clear()


@router.message(VisionStates.waiting_for_image)
async def state_vision_invalid_input_handler(message: Message):
    """
    Handles unsupported content (text, stickers, etc.) when the bot is waiting for an image.
    Sends a message to the user asking them to send an image.
    """
    await message.answer("I'm sorry, I can only generate descriptions for images.")
