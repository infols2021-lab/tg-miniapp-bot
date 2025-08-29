import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем, что токен есть
if not BOT_TOKEN:
    exit("Ошибка: не задан BOT_TOKEN")

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера с новым синтаксисом
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Этот обработчик вызывается на команду /start
    """
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! Добро пожаловать в бота!")

# Главная функция
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())