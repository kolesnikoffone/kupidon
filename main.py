import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # должен быть строкой

bot = Bot(token=BOT_TOKEN)
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

user_data = {}

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Давай заполним приглашение на свадьбу 💍\nКак тебя зовут? (Имя и Фамилия)")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    await message.answer("Будут ли с вами дополнительные гости?", reply_markup=markup)
    await state.set_state(Form.has_guests)

@dp.message(Form.has_guests)
async def has_guests(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await state.set_state(Form.guest_count)
        await message.answer("Сколько человек будет с вами?")
    else:
        await state.update_data(guest_names=[])
        await ask_main_course(message, state)

@dp.message(Form.guest_count)
async def get_guest_count(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        await state.update_data(guest_count=count, guest_names=[])
        await message.answer("Пожалуйста, введите имя каждого гостя по одному сообщению")
        await state.set_state(Form.guest_names)
    except ValueError:
        await message.answer("Введите число, пожалуйста")

@dp.message(Form.guest_names)
async def get_guest_names(message: types.Message, state: FSMContext):
    data = await state.get_data()
    guest_names = data.get("guest_names", [])
    guest_names.append(message.text)
    if len(guest_names) < data["guest_count"]:
        await state.update_data(guest_names=guest_names)
        await message.answer("Введите следующее имя")
    else:
        await state.update_data(guest_names=guest_names)
        await ask_main_course(message, state)

async def ask_main_course(message: types.Message, state: FSMContext):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рыба", callback_data="food:Рыба")],
        [InlineKeyboardButton(text="Мясо", callback_data="food:Мясо")],
        [InlineKeyboardButton(text="Курица", callback_data="food:Курица")],
        [InlineKeyboardButton(text="Овощи и грибы", callback_data="food:Овощи и грибы")],
    ])
    await message.answer("Что вы предпочитаете в качестве основного блюда?", reply_markup=markup)
    await state.set_state(Form.main_course)

@dp.callback_query(lambda c: c.data.startswith("food:"))
async def food_chosen(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await state.update_data(main_course=choice)
    await callback.message.answer("Выберите предпочтения по алкоголю (можно несколько, отправьте одним сообщением):\nИгристое, Белое вино, Красное вино, Коньяк, Водка, Другое")
    await state.set_state(Form.alcohol)
    await callback.answer()

@dp.message(Form.alcohol)
async def get_alcohol(message: types.Message, state: FSMContext):
    alcohol_choices = [s.strip() for s in message.text.split(",")]
    await state.update_data(alcohol=alcohol_choices)
    await message.answer("Если у вас есть комментарии, напишите их сейчас. Или отправьте '-' чтобы пропустить")
    await state.set_state(Form.comment)

@dp.message(Form.comment)
async def get_comment(message: types.Message, state: FSMContext):
    comment = message.text if message.text.strip() != "-" else "(без комментариев)"
    await state.update_data(comment=comment)
    data = await state.get_data()

    guest_block = "\n".join(data.get("guest_names", [])) if data.get("guest_names") else "нет"
    alcohol_str = ", ".join(data.get("alcohol", []))

    summary = (
        f"📨 Новое подтверждение:\n"
        f"👤 Имя: {data['name']}\n"
        f"👥 Доп. гости: {guest_block}\n"
        f"🍽 Блюдо: {data['main_course']}\n"
        f"🍷 Алкоголь: {alcohol_str}\n"
        f"💬 Комментарий: {data['comment']}"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
    await message.answer("Спасибо за ответы! Присоединяйся к свадебному чату 🎉\nhttps://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
