# handlers/image.py
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.image import get_image_interface_keyboard
from states.bot_states import VisionStates
from services.openai_client import openai_client
from utils.logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(Command("image"))
async def command_image_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the /image command.
    Clears the current state and sets it to waiting for an image.
    Sends a message to the user asking them to send an image.
    """
    await state.clear()
    await state.set_state(VisionStates.waiting_for_image)
    await message.answer(
        "Send me an image and I'll generate a description for it!",
        reply_markup=get_image_interface_keyboard(),
    )


@router.callback_query(F.data == "image")
async def image_start_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the image callback query.
    Clears the current state and sets it to waiting for an image.
    Sends a message to the user asking them to send an image.
    """
    await callback.answer()
    await state.clear()
    await state.set_state(VisionStates.waiting_for_image)
    await callback.message.answer(
        "Send me an image and I'll generate a description for it!",
    )


@router.message(VisionStates.waiting_for_image, F.photo | F.document)
async def handle_image(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Handles the image message.
    Downloads the image and generates a caption for it using the OpenAI API.
    Sends the caption back to the user and clears the current state.
    """
    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        if message.document.mime_type and "image" in message.document.mime_type:
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

        prompt = "Create a short description for this image"
        caption = await openai_client.describe_image(
            image_bytes=image_bytes, prompt=prompt
        )

        if caption:
            await status_message.edit_text(caption)
        else:
            await status_message.edit_text(
                "Unfortunately, I could not generate a caption for this image."
            )

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await status_message.edit_text("An error occurred while processing the image.")
    finally:
        await state.clear()


@router.message(VisionStates.waiting_for_image)
async def handle_unsupported_content(message: Message):
    """
    Handles unsupported content (text, stickers, etc.) when the bot is waiting for an image.
    Sends a message to the user asking them to send an image.
    """
    await message.answer("I'm sorry, I can only generate descriptions for images.")
