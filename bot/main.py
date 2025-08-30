import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.markdown import hbold
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from database import create_user, get_user_by_tg_id, initialize_user_tasks

# Загружаем переменные из .env файла
load_dotenv()

# Получаем все переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEB_APP_URL = os.getenv("WEB_APP_URL")

# Проверяем обязательные переменные
if not BOT_TOKEN:
    exit("Ошибка: не задан BOT_TOKEN")
if not SUPABASE_URL:
    exit("Ошибка: не задан SUPABASE_URL")
if not SUPABASE_KEY:
    exit("Ошибка: не задан SUPABASE_KEY")
if not WEB_APP_URL:
    print("Предупреждение: не задан WEB_APP_URL, Mini Apps не будет работать")

# Включаем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Определяем состояния для регистрации
class Registration(StatesGroup):
    first_name = State()
    last_name = State()

# Создаем клавиатуру с кнопкой для Mini Apps
def get_main_keyboard():
    if WEB_APP_URL:
        web_app = WebAppInfo(url=WEB_APP_URL)
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Открыть Mini App", web_app=web_app)]],
            resize_keyboard=True
        )
    return None

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start"""
    tg_id = message.from_user.id
    logger.info(f"Пользователь {tg_id} запустил бота")
    
    # Проверяем, есть ли пользователь в базе
    user = await get_user_by_tg_id(tg_id)
    
    if user:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"С возвращением, {hbold(user['first_name'])} {hbold(user['last_name'])}!\n\n"
            "Используйте кнопку меню для доступа к приложению.",
            reply_markup=get_main_keyboard()
        )
    else:
        # Новый пользователь - начинаем процесс регистрации
        await message.answer(
            "👋 Добро пожаловать! Похоже, вы здесь впервые.\n\n"
            "Для регистрации в системе мне нужно узнать ваше имя и фамилию.\n\n"
            "Пожалуйста, введите ваше имя:",
            reply_markup=ReplyKeyboardRemove()
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
            "Теперь вы можете перейти к заданиям, используя кнопку ниже.",
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Зарегистрирован новый пользователь: {first_name} {last_name} (ID: {tg_id})")
    else:
        await message.answer(
            "❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
        logger.error(f"Ошибка регистрации для пользователя {tg_id}")
    
    await state.clear()

# Обработчик текстовых сообщений
@dp.message(F.text == "📱 Открыть Mini App")
async def open_mini_app(message: Message):
    """Обработчик кнопки открытия Mini App"""
    if WEB_APP_URL:
        web_app = WebAppInfo(url=WEB_APP_URL)
        await message.answer(
            "Открываю приложение...",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Открыть Mini App", web_app=web_app)]],
                resize_keyboard=True
            )
        )
    else:
        await message.answer("Приложение временно недоступно. Приносим извинения за неудобства.")

# Обработчик любых других сообщений
@dp.message()
async def other_messages_handler(message: Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Используйте команду /start для регистрации или кнопку ниже для открытия приложения.",
        reply_markup=get_main_keyboard()
    )

# Главная функция
async def main() -> None:
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())