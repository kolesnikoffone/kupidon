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
    comment = State()

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    start_button = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Начать", callback_data="start_form")]])
    await message.answer("Привет! Я Купидончик 💘\nГотов(а) ответить на пару вопросов, чтобы подтвердить участие в свадьбе?", reply_markup=start_button)

@dp.callback_query(lambda c: c.data == "start_form")
async def handle_start_form(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("Как тебя зовут? (Имя и Фамилия)")
    await state.set_state(Form.name)
    await callback.answer()

@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="guests_yes")],
        [InlineKeyboardButton(text="Нет", callback_data="guests_no")]
    ])
    await message.answer("Будут ли с вами дополнительные гости?", reply_markup=keyboard)
    await state.set_state(Form.has_guests)

@dp.callback_query(lambda c: c.data in ["guests_yes", "guests_no"])
async def handle_guest_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "guests_yes":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1", callback_data="guest_count:1")],
            [InlineKeyboardButton(text="2", callback_data="guest_count:2")],
            [InlineKeyboardButton(text="3", callback_data="guest_count:3")]
        ])
        await callback.message.edit_text("Сколько человек будет с вами?", reply_markup=keyboard)
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
        await callback.message.edit_text("Введите имя гостя")
    else:
        await callback.message.edit_text("Введите имена гостей через запятую")
    await state.set_state(Form.guest_names)
    await callback.answer()

@dp.message(Form.guest_names)
async def get_guest_names(message: types.Message, state: FSMContext):
    data = await state.get_data()
    names = [name.strip() for name in message.text.split(",") if name.strip()]
    await state.update_data(guest_names=names)
    await ask_main_course(message, state)

async def ask_main_course(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рыба", callback_data="food:Рыба")],
        [InlineKeyboardButton(text="Мясо", callback_data="food:Мясо")],
        [InlineKeyboardButton(text="Курица", callback_data="food:Курица")],
        [InlineKeyboardButton(text="Овощи и грибы", callback_data="food:Овощи и грибы")]
    ])
    await message.answer("Что вы предпочитаете в качестве основного блюда? (можно выбрать несколько)", reply_markup=keyboard)
    await state.update_data(main_course=[])
    await state.set_state(Form.main_course)

@dp.callback_query(lambda c: c.data.startswith("food:"))
async def select_food(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("main_course", [])
    if choice not in selected:
        selected.append(choice)
    await state.update_data(main_course=selected)
    await callback.answer(text=f"Добавлено: {choice}")
    await callback.message.answer("Можете выбрать ещё блюдо или нажмите 'Далее'", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Далее", callback_data="done_food")]]))

@dp.callback_query(lambda c: c.data == "done_food")
async def ask_alcohol(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Игристое", callback_data="alc:Игристое")],
        [InlineKeyboardButton(text="Белое вино", callback_data="alc:Белое вино")],
        [InlineKeyboardButton(text="Красное вино", callback_data="alc:Красное вино")],
        [InlineKeyboardButton(text="Коньяк", callback_data="alc:Коньяк")],
        [InlineKeyboardButton(text="Водка", callback_data="alc:Водка")],
        [InlineKeyboardButton(text="Другое", callback_data="alc:Другое")]
    ])
    await callback.message.edit_text("Предпочтения по алкоголю (можно выбрать несколько)", reply_markup=keyboard)
    await state.update_data(alcohol=[])
    await state.set_state(Form.alcohol)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("alc:"))
async def select_alcohol(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("alcohol", [])
    if choice not in selected:
        selected.append(choice)
    await state.update_data(alcohol=selected)
    await callback.message.answer("Можете выбрать ещё напиток или нажмите 'Далее'", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Далее", callback_data="done_alcohol")]]))
    await callback.answer(text=f"Добавлено: {choice}")

@dp.callback_query(lambda c: c.data == "done_alcohol")
async def ask_comment(callback: types.CallbackQuery, state: FSMContext):
    skip_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_comment")]
    ])
    await callback.message.edit_text("Если у вас есть комментарии, напишите их одним сообщением или нажмите кнопку ниже.", reply_markup=skip_button)
    await state.set_state(Form.comment)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "skip_comment")
async def skip_comment(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(comment="(без комментариев)")
    await finish(callback.message, state)
    await callback.answer()

@dp.message(Form.comment)
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

    await message.answer("Спасибо! Присоединяйся к свадебному чату 🎉\nhttps://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
