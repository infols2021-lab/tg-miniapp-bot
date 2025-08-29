import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from database import create_user, get_user_by_tg_id, initialize_user_tasks

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

# Определяем состояния для регистрации
class Registration(StatesGroup):
    first_name = State()
    last_name = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start"""
    tg_id = message.from_user.id
    
    # Проверяем, есть ли пользователь в базе
    user = await get_user_by_tg_id(tg_id)
    
    if user:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"С возвращением, {hbold(user['first_name'])} {hbold(user['last_name'])}!\n\n"
            "Используйте кнопку меню или введите /menu для доступа к функциям бота."
        )
    else:
        # Новый пользователь - начинаем процесс регистрации
        await message.answer(
            "👋 Добро пожаловать! Похоже, вы здесь впервые.\n\n"
            "Для регистрации в системе мне нужно узнать ваше имя и фамилию.\n\n"
            "Пожалуйста, введите ваше имя:"
        )
        await state.set_state(Registration.first_name)

# Обработчик ввода имени
@dp.message(Registration.first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    """Обработчик ввода имени"""
    first_name = message.text.strip()
    
    if len(first_name) < 2:
        await message.answer("Имя должно содержать хотя бы 2 символа. Попробуйте еще раз:")
        return
    
    await state.update_data(first_name=first_name)
    await message.answer("Теперь введите вашу фамилию:")
    await state.set_state(Registration.last_name)

# Обработчик ввода фамилии
@dp.message(Registration.last_name)
async def process_last_name(message: Message, state: FSMContext) -> None:
    """Обработчик ввода фамилии"""
    last_name = message.text.strip()
    
    if len(last_name) < 2:
        await message.answer("Фамилия должна содержать хотя бы 2 символа. Попробуйте еще раз:")
        return
    
    user_data = await state.get_data()
    first_name = user_data['first_name']
    tg_id = message.from_user.id
    
    # Создаем пользователя в базе данных
    user = await create_user(tg_id, first_name, last_name)
    
    if user:
        # Инициализируем задачи для пользователя
        await initialize_user_tasks(user['id'])
        
        await message.answer(
            f"✅ Регистрация завершена!\n\n"
            f"Добро пожаловать, {hbold(first_name)} {hbold(last_name)}!\n\n"
            "Теперь вы можете перейти к заданиям, используя кнопку меню.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
    
    await state.clear()

# Главная функция
async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())