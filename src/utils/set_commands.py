# utils/set_commands.py
from aiogram import Bot
from aiogram.types import BotCommand


async def set_commands(bot: Bot) -> None:
    """
    Sets the bot's commands menu.

    Args:
        bot: The bot instance
    """
    commands = [
        BotCommand(command="/start", description="🚀 Start the bot and show main menu"),
        BotCommand(command="/help", description="❓ Get help and instructions"),
    ]

    await bot.set_my_commands(commands)
