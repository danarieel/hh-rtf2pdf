import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import FSInputFile
from src.parser import parse_hh_rtf
from src.pdf_generator import generate_pdf

# Загружаем настройки
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
PROXY_URL = os.getenv("PROXY_URL")

if not TOKEN:
    raise ValueError("Ошибка: TELEGRAM_TOKEN не найден в .env")

# Создаем папки, если их нет
for folder in ["input", "output"]:
    Path(folder).mkdir(exist_ok=True)

# Настройка сессии (с прокси или без)
session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я конвертер резюме.\n"
        "Скачай свое резюме с hh.ru в формате **RTF** и отправь мне сюда файлом.\n"
        "Я переделаю его в красивый темный PDF."
    )

@dp.message(F.document)
async def handle_document(message: types.Message):
    doc = message.document
    if not doc.file_name.endswith(".rtf"):
        await message.answer("Пожалуйста, отправь файл в формате .rtf (его можно скачать с hh.ru).")
        return

    status_msg = await message.answer("⏳ Обрабатываю файл...")

    # Пути для файлов
    input_path = Path("input") / f"{message.from_user.id}_{doc.file_name}"
    output_pdf = Path("output") / f"CV_{message.from_user.id}.pdf"

    try:
        # 1. Скачиваем файл из Telegram
        await bot.download(doc, destination=input_path)

        # 2. Парсим RTF
        data = parse_hh_rtf(str(input_path))

        # 3. Генерируем PDF
        generate_pdf(data, str(output_pdf))

        # 4. Отправляем готовый PDF
        await message.answer_document(
            FSInputFile(str(output_pdf)), 
            caption="✅ Готово! Твое резюме переупаковано."
        )
        
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка при обработке файла.\nЛог: {e}")
    finally:
        # Очищаем временные файлы
        if input_path.exists():
            input_path.unlink()
        if output_pdf.exists():
            output_pdf.unlink()
        await status_msg.delete()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())