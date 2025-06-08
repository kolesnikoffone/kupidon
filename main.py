import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    start_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать", callback_data="start_form")]
    ])

    await bot.send_photo(
        chat_id=message.chat.id,
        photo="https://i.postimg.cc/MTf0j1W2/IMG-6156-EDIT.jpg",
        caption=(
            "💍 <b>Свадьба Игоря и Анастасии</b>\n\n"
            "📅 <b>Дата:</b> 23 июля 2025\n"
            "🕛 <b>Время:</b> 12:00 — регистрация\n"
            "📍 <b>Регистрация:</b> <a href='https://yandex.ru/maps/-/CHrU5XZ4'>Екатерининский зал</a>\n"
            "🍽 <b>Банкет:</b> <a href='https://yandex.ru/maps/-/CHrUBE2i'>Двин Холл, зал Лайт</a>\n"
            "👗 <b>Дресс-код:</b> классика в пастельных тонах (не строго)"
        ),
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        "Привет! Я Купидончик 💘\nГотов(а) ответить на пару вопросов, чтобы подтвердить участие в свадьбе?",
        reply_markup=start_button
    )

@dp.callback_query(lambda c: c.data == "start_form")
async def handle_start_form(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("👤 Как тебя зовут? (Имя и Фамилия)")
    await state.set_state(Form.name)
    await callback.answer()

@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await ask_main_course(message, state)

async def ask_main_course(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐟 Рыба", callback_data="food:Рыба")],
        [InlineKeyboardButton(text="🥩 Мясо", callback_data="food:Мясо")],
        [InlineKeyboardButton(text="🍗 Курица", callback_data="food:Курица")],
        [InlineKeyboardButton(text="🥦 Овощи и грибы", callback_data="food:Овощи и грибы")]
    ])
    await message.answer("🍽 Что вы предпочитаете в качестве основного блюда?", reply_markup=keyboard)
    await state.set_state(Form.main_course)

@dp.callback_query(lambda c: c.data.startswith("food:"))
async def select_food(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await state.update_data(main_course=[choice])
    await callback.message.answer(f"✅ Вы выбрали: {choice}")
    await ask_alcohol(callback.message, state)
    await callback.answer()

async def ask_alcohol(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍾 Игристое", callback_data="alc:Игристое")],
        [InlineKeyboardButton(text="🥂 Белое вино", callback_data="alc:Белое вино")],
        [InlineKeyboardButton(text="🍷 Красное вино", callback_data="alc:Красное вино")],
        [InlineKeyboardButton(text="🥃 Коньяк", callback_data="alc:Коньяк")],
        [InlineKeyboardButton(text="🍸 Водка", callback_data="alc:Водка")],
        [InlineKeyboardButton(text="🧃 Другое", callback_data="alc:Другое")],
        [InlineKeyboardButton(text="📝 Пропустить", callback_data="skip_alcohol")]
    ])
    await message.answer("🍷 Предпочтения по алкоголю:", reply_markup=keyboard)
    await state.set_state(Form.alcohol)

@dp.callback_query(lambda c: c.data.startswith("alc:"))
async def select_alcohol(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await callback.message.answer(f"✅ Вы выбрали: {choice}")
    if choice == "Другое":
        await callback.message.answer("✍️ Пожалуйста, напишите, что именно вы предпочитаете из напитков")
        await state.set_state(Form.alcohol_other)
    else:
        await state.update_data(alcohol=[choice])
        await finish(callback.message, state)
    await callback.answer()

@dp.message(Form.alcohol_other)
async def handle_other_alcohol(message: types.Message, state: FSMContext):
    other = message.text.strip()
    data = await state.get_data()
    alcohol = data.get("alcohol", [])
    alcohol.append(other)
    await state.update_data(alcohol=alcohol)
    await finish(message, state)

@dp.callback_query(lambda c: c.data == "skip_alcohol")
async def skip_alcohol(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(alcohol=["(не выбрано)"])
    await callback.message.answer("✅ Вы выбрали: (не выбрано)")
    await finish(callback.message, state)
    await callback.answer()

async def finish(message: types.Message, state: FSMContext):
    data = await state.get_data()

    summary = (
        f"<b>📨 Новое подтверждение:</b>\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"🍽 <b>Блюдо:</b> {', '.join(data.get('main_course', []))}\n"
        f"🍷 <b>Алкоголь:</b> {', '.join(data.get('alcohol', []))}"
    )

    if not ADMIN_CHAT_ID:
        await message.answer("❌ ADMIN_CHAT_ID не задан. Пожалуйста, проверь настройки на Render.")
        return
    try:
        await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=summary)
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке сообщения в чат: {e}")

    await message.answer("🎉 Спасибо! Присоединяйся к свадебному чату: https://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
