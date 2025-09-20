import asyncio
from os import getenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from middlewares import include_middlewares
from handlers import include_routers
from utils.set_commands import set_commands
from utils.logger import get_logger

# Load environment variables
load_dotenv()
TOKEN = getenv("BOT_TOKEN")
logger = get_logger(__name__)

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

# Initialize dispatcher with FSM storage
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Include all routers and middlewares
include_routers(dp)
include_middlewares(dp)


async def on_startup(bot: Bot) -> None:
    """Actions to perform on bot startup."""
    logger.info("Bot is starting up...")
    await set_commands(bot)
    # commands = await bot.get_my_commands()
    # logger.info(f"Bot commands: {commands}")
    logger.info("Bot commands set successfully.")

    logger.info("Bot started successfully.")


async def on_shutdown(bot: Bot) -> None:
    """Actions to perform on bot shutdown."""
    logger.info("Bot is shutting down...")


async def main() -> None:
    """Main entry point of the bot."""
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables.")

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
