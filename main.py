import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    main_course = State()
    alcohol = State()
    alcohol_other = State()
    comment = State()

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_photo(
        chat_id=message.chat.id,
        photo="https://i.postimg.cc/YCJ77THc/photo-2025-06-08-18-34-47.jpg",
        caption=(
            "💍 <b>Свадьба Игоря и Анастасии</b>\n\n"
            "📅 <b>Дата:</b> 23 июля 2025\n"
            "🕛 <b>Время:</b> 12:00 — регистрация\n"
            "📍 <b>Регистрация:</b> <a href='https://yandex.ru/maps/-/CHrU5XZ4'>Екатерининский зал</a>\n"
            "🍽 <b>Банкет:</b> <a href='https://yandex.ru/maps/-/CHrUBE2i'>Двин Холл, зал Лайт</a>\n"
            "👗 <b>Дресс-код:</b> классика в пастельных тонах (не строго)\n\n"
            "Привет! Я Купидончик 💘\nГотов(а) ответить на пару вопросов, чтобы подтвердить участие в свадьбе?"
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать", callback_data="start_form")],
            [InlineKeyboardButton(
                text="📅 Добавить в календарь",
                url="https://www.google.com/calendar/render?action=TEMPLATE&text=Свадьба+Игоря+и+Анастасии&dates=20250723T120000/20250723T160000&ctz=Europe/Moscow&details=Регистрация:+https://yandex.ru/maps/-/CHrU5XZ4+%0AБанкет:+https://yandex.ru/maps/-/CHrUBE2i+%0AДресс-код:+классика+в+пастельных+тонах&location=Екатерининский+зал,+Двин+Холл"
            )]
        ]),
        parse_mode=ParseMode.HTML
    )
