import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # строка с chat_id вида -100...

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
    await message.answer("Привет! Давай заполним приглашение на свадьбу 💍\nКак тебя зовут? (Имя и Фамилия)")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да")],[KeyboardButton(text="Нет")]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Будут ли с вами дополнительные гости?", reply_markup=keyboard)
    await state.set_state(Form.has_guests)

@dp.message(Form.has_guests)
async def ask_guest_count(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == "да":
        await message.answer("Сколько человек будет с вами?", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Form.guest_count)
    else:
        await state.update_data(guest_names=[])
        await ask_main_course(message, state)

@dp.message(Form.guest_count)
async def get_guest_count(message: types.Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        await state.update_data(guest_count=count, guest_names=[])
        await message.answer("Введите имя каждого гостя по одному сообщению")
        await state.set_state(Form.guest_names)
    except ValueError:
        await message.answer("Пожалуйста, введите число гостей цифрой")

@dp.message(Form.guest_names)
async def get_guest_names(message: types.Message, state: FSMContext):
    data = await state.get_data()
    guests = data.get("guest_names", [])
    guests.append(message.text.strip())
    if len(guests) < data.get("guest_count", 0):
        await state.update_data(guest_names=guests)
        await message.answer("Введите следующее имя")
    else:
        await state.update_data(guest_names=guests)
        await ask_main_course(message, state)

async def ask_main_course(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    for food in ["Рыба", "Мясо", "Курица", "Овощи и грибы"]:
        builder.button(text=food, callback_data=f"food:{food}")
    await message.answer("Что вы предпочитаете в качестве основного блюда?", reply_markup=builder.as_markup())
    await state.set_state(Form.main_course)

@dp.callback_query(lambda c: c.data.startswith("food:"))
async def get_food(callback: types.CallbackQuery, state: FSMContext):
    food_choice = callback.data.split(":")[1]
    await state.update_data(main_course=food_choice)
    await callback.message.edit_reply_markup()
    await callback.message.answer("Предпочтения по алкоголю (можно несколько, отправьте одним сообщением):\nИгристое, Белое вино, Красное вино, Коньяк, Водка, Другое")
    await state.set_state(Form.alcohol)
    await callback.answer()

@dp.message(Form.alcohol)
async def get_alcohol(message: types.Message, state: FSMContext):
    choices = [c.strip() for c in message.text.split(",") if c.strip()]
    await state.update_data(alcohol=choices)
    skip_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_comment")]
    ])
    await message.answer("Если у вас есть комментарии, напишите их сейчас или нажмите кнопку ниже.", reply_markup=skip_button)
    await state.set_state(Form.comment)

@dp.callback_query(lambda c: c.data == "skip_comment")
async def skip_comment(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(comment="(без комментариев)")
    await finish(callback.message, state)
    await callback.answer()

@dp.message(Form.comment)
async def finish(message: types.Message, state: FSMContext):
    data = await state.update_data(comment=message.text.strip())
    data = await state.get_data()

    summary = f"<b>📨 Новое подтверждение:</b>\n"
    summary += f"👤 <b>Имя:</b> {data['name']}\n"
    summary += f"👥 <b>Доп. гости:</b> {', '.join(data.get('guest_names', ['нет']))}\n"
    summary += f"🍽 <b>Блюдо:</b> {data['main_course']}\n"
    summary += f"🍷 <b>Алкоголь:</b> {', '.join(data.get('alcohol', []))}\n"
    summary += f"💬 <b>Комментарий:</b> {data['comment']}"

    await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=summary)
    await message.answer("Спасибо! Присоединяйся к свадебному чату 🎉\nhttps://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
