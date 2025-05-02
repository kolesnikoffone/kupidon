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
    has_guests = State()
    guest_count = State()
    guest_names = State()
    main_course = State()
    alcohol = State()
    alcohol_other = State()
    comment = State()

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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👍 Да", callback_data="guests_yes")],
        [InlineKeyboardButton(text="🙅‍♂️ Нет", callback_data="guests_no")]
    ])
    await message.answer("👥 Будут ли с вами дополнительные гости?", reply_markup=keyboard)
    await state.set_state(Form.has_guests)

@dp.callback_query(lambda c: c.data in ["guests_yes", "guests_no"])
async def handle_guest_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "guests_yes":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1", callback_data="guest_count:1"), InlineKeyboardButton(text="2", callback_data="guest_count:2"), InlineKeyboardButton(text="3", callback_data="guest_count:3")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back:name")]
        ])
        await callback.message.edit_text("🧑‍🤝‍🧑 Сколько человек будет с вами?", reply_markup=keyboard)
        await state.set_state(Form.guest_count)
    else:
        await state.update_data(guest_names=[])
        await ask_main_course(callback.message, state)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("guest_count:"))
async def handle_guest_count(callback: types.CallbackQuery, state: FSMContext):
    count = int(callback.data.split(":")[1])
    await state.update_data(guest_count=count, guest_names=[])
    if count == 1:
        await callback.message.edit_text("✍️ Введите имя гостя")
    else:
        await callback.message.edit_text("✍️ Введите имена гостей через запятую")
    await state.set_state(Form.guest_names)
    await callback.answer()

@dp.message(Form.guest_names)
async def get_guest_names(message: types.Message, state: FSMContext):
    names = [name.strip() for name in message.text.split(",") if name.strip()]
    await state.update_data(guest_names=names)
    await ask_main_course(message, state)

async def ask_main_course(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐟 Рыба", callback_data="food:Рыба")],
        [InlineKeyboardButton(text="🥩 Мясо", callback_data="food:Мясо")],
        [InlineKeyboardButton(text="🍗 Курица", callback_data="food:Курица")],
        [InlineKeyboardButton(text="🥦 Овощи и грибы", callback_data="food:Овощи и грибы")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:guests")]
    ])
    await message.answer("🍽 Что вы предпочитаете в качестве основного блюда?", reply_markup=keyboard)
    await state.set_state(Form.main_course)

@dp.callback_query(lambda c: c.data.startswith("food:"))
async def select_food(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await state.update_data(main_course=[choice])
    await ask_alcohol(callback.message, state)
    await callback.answer()

async def ask_alcohol(message: types.Message, state: FSMContext):

async def ask_comment(message: types.Message, state: FSMContext):
    await finish(message, state)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍾 Игристое", callback_data="alc:Игристое")],
        [InlineKeyboardButton(text="🥂 Белое вино", callback_data="alc:Белое вино")],
        [InlineKeyboardButton(text="🍷 Красное вино", callback_data="alc:Красное вино")],
        [InlineKeyboardButton(text="🥃 Коньяк", callback_data="alc:Коньяк")],
        [InlineKeyboardButton(text="🍸 Водка", callback_data="alc:Водка")],
        [InlineKeyboardButton(text="🧃 Другое", callback_data="alc:Другое")],
        [InlineKeyboardButton(text="📝 Пропустить", callback_data="skip_alcohol")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:main_course")]
    ])
    await message.answer("🍷 Предпочтения по алкоголю (выберите один):", reply_markup=keyboard)
    await state.update_data(alcohol=[])
    await state.set_state(Form.alcohol)

@dp.callback_query(lambda c: c.data.startswith("alc:"))
async def select_alcohol(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    if choice == "Другое":
        await callback.message.answer("✍️ Пожалуйста, напишите, что именно вы предпочитаете из напитков")
        await state.set_state(Form.alcohol_other)
    else:
        await state.update_data(alcohol=[choice])
        await ask_comment(callback.message, state)
    await callback.answer()

@dp.message(Form.alcohol_other)
async def handle_other_alcohol(message: types.Message, state: FSMContext):
    other = message.text.strip()
    data = await state.get_data()
    alcohol = data.get("alcohol", [])
    alcohol.append(other)
    await state.update_data(alcohol=alcohol)
    await ask_comment(message, state)
    await state.set_state(Form.comment)

@dp.callback_query(lambda c: c.data.startswith("back:"))
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "back:name":
        await callback.message.edit_text("👤 Как тебя зовут? (Имя и Фамилия)")
        await state.set_state(Form.name)
    elif callback.data == "back:guests":
        await get_name(callback.message, state)
    elif callback.data == "back:main_course":
        await ask_main_course(callback.message, state)
    elif callback.data == "back:alcohol":
        await ask_alcohol(callback.message, state)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "skip_alcohol")
async def skip_alcohol(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(alcohol=["(не выбрано)"])
    await ask_comment(callback.message, state)
    await callback.answer()
    await callback.answer()

@dp.message(Form.alcohol)
async def finish(message: types.Message, state: FSMContext):
    data = await state.update_data(comment=message.text.strip())
    data = await state.get_data()

    summary = (
        f"<b>📨 Новое подтверждение:</b>\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"👥 <b>Доп. гости:</b> {', '.join(data.get('guest_names', ['нет']))}\n"
        f"🍽 <b>Блюдо:</b> {', '.join(data.get('main_course', []))}\n"
        f"🍷 <b>Алкоголь:</b> {', '.join(data.get('alcohol', []))}\n"
        f"💬 <b>Комментарий:</b> {data['comment']}"
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
