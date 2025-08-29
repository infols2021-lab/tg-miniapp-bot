import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Инициализация Supabase клиента
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def create_user(tg_id: int, first_name: str, last_name: str):
    """Создание нового пользователя в базе данных"""
    try:
        user_data = {
            "tg_id": tg_id,
            "first_name": first_name,
            "last_name": last_name,
            "keys_count": 0
        }
        
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        return None

async def get_user_by_tg_id(tg_id: int):
    """Получение пользователя по Telegram ID"""
    try:
        response = supabase.table("users").select("*").eq("tg_id", tg_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None

async def initialize_user_tasks(user_id: int):
    """Инициализация задач для нового пользователя"""
    try:
        tasks = [
            {"user_id": user_id, "task_name": "сентябрь", "status": "not_started"},
            {"user_id": user_id, "task_name": "октябрь", "status": "not_started"},
            {"user_id": user_id, "task_name": "ноябрь", "status": "not_started"},
            {"user_id": user_id, "task_name": "декабрь", "status": "not_started"},
            {"user_id": user_id, "task_name": "январь", "status": "not_started"},
            {"user_id": user_id, "task_name": "февраль", "status": "not_started"},
            {"user_id": user_id, "task_name": "март", "status": "not_started"}
        ]
        
        response = supabase.table("user_tasks").insert(tasks).execute()
        return response.data if response.data else None
    except Exception as e:
        print(f"Ошибка при инициализации задач: {e}")
        return None