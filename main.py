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

# Init bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# Define states
class Form(StatesGroup):
    name = State()
    main_course = State()
    alcohol = State()
    activities = State()
    transport = State()
    dance = State()

# /start handler
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать", callback_data="start_form")],
        [InlineKeyboardButton(text="📅 Добавить в календарь", url=
            "https://www.google.com/calendar/render?action=TEMPLATE&text=Свадьба+Игоря+и+Анастасии&"
            "dates=20250723T120000/20250723T160000&ctz=Europe/Moscow"
            "&details=Регистрация:+https://yandex.ru/maps/-/CHrU5XZ4%0AБанкет:+https://yandex.ru/maps/-/CHrUBE2i"
            "%0AДресс-код:+классика+в+пастельных+тонах&location=Екатерининский+зал,+Двин+Холл"
        )]
    ])
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
            "Привет! Я Купидончик 💘\nГотов(а) ответить на вопросы?"
        ),
        reply_markup=markup
    )

# back handler
@dp.callback_query(lambda c: c.data.startswith("back:"))
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    step = callback.data.split(":")[1]
    await callback.message.delete()
    if step == "name":
        await start(callback.message, state)
    elif step == "main_course":
        await get_name(callback.message, state)
    elif step == "alcohol":
        await select_main_course(callback, state)
    elif step == "activities":
        await select_alcohol(callback, state)
    elif step == "transport":
        await select_activities(callback, state)
    elif step == "dance":
        await select_transport(callback, state)
    await callback.answer()

# start form
@dp.callback_query(lambda c: c.data == "start_form")
async def handle_start_form(callback: types.CallbackQuery, state: FSMContext):
    cal_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Добавить в календарь", url=
            "https://www.google.com/calendar/render?action=TEMPLATE&text=Свадьба+Игоря+и+Анастасии&"
            "dates=20250723T120000/20250723T160000&ctz=Europe/Moscow"
            "&details=Регистрация:+https://yandex.ru/maps/-/CHrU5XZ4%0AБанкет:+https://yandex.ru/maps/-/CHrUBE2i"
            "%0AДресс-код:+классика+в+пастельных+тонах&location=Екатерининский+зал,+Двин+Холл"
        )]
    ])
    await callback.message.edit_reply_markup(reply_markup=cal_markup)
    await callback.message.answer("👤 Как тебя зовут? (Имя и Фамилия)")
    await state.set_state(Form.name)

# name
@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐟 Рыба", callback_data="food:Рыба")],
        [InlineKeyboardButton(text="🥩 Мясо", callback_data="food:Мясо")],
        [InlineKeyboardButton(text="🍗 Курица", callback_data="food:Курица")],
        [InlineKeyboardButton(text="🥦 Овощи и грибы", callback_data="food:Овощи и грибы")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:name")]
    ])
    await message.answer("🍽 Какое основное блюдо вы предпочитаете?", reply_markup=keyboard)
    await state.set_state(Form.main_course)

# main course
@dp.callback_query(lambda c: c.data.startswith("food:"))
async def select_main_course(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"✅ Вы выбрали: {choice}")
    await state.update_data(main_course=choice)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍾 Игристое", callback_data="alc:Игристое")],
        [InlineKeyboardButton(text="🥂 Белое вино", callback_data="alc:Белое вино")],
        [InlineKeyboardButton(text="🍷 Красное вино", callback_data="alc:Красное вино")],
        [InlineKeyboardButton(text="🥃 Коньяк", callback_data="alc:Коньяк")],
        [InlineKeyboardButton(text="🍸 Водка", callback_data="alc:Водка")],
        [InlineKeyboardButton(text="📝 Пропустить", callback_data="alc:Пропустить")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:main_course")]
    ])
    await callback.message.answer("🍷 Предпочтения по алкоголю?", reply_markup=keyboard)
    await state.set_state(Form.alcohol)

# alcohol
@dp.callback_query(lambda c: c.data.startswith("alc:"))
async def select_alcohol(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"✅ Вы выбрали: {choice}")
    await state.update_data(alcohol=choice)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎉 Да, очень хочу!", callback_data="act:yes")],
        [InlineKeyboardButton(text="🤔 Может быть", callback_data="act:maybe")],
        [InlineKeyboardButton(text="🍽 Я хочу покушать", callback_data="act:no")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:alcohol")]
    ])
    await callback.message.answer("🎭 Хотите ли участвовать в активностях?", reply_markup=keyboard)
    await state.set_state(Form.activities)

# activities
@dp.callback_query(lambda c: c.data.startswith("act:"))
async def select_activities(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    mapping = {"yes":"Да, очень хочу!","maybe":"Может быть","no":"Я хочу покушать"}
    text = mapping.get(key)
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"✅ Вы выбрали: {text}")
    await state.update_data(activities=text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚗 На машине", callback_data="trans:car")],
        [InlineKeyboardButton(text="🚕 На такси", callback_data="trans:taxi")],
        [InlineKeyboardButton(text="🐴 На коне", callback_data="trans:horse")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:activities")]
    ])
    await callback.message.answer("🚙 Каким транспортом доберетесь?", reply_markup=keyboard)
    await state.set_state(Form.transport)

# transport
@dp.callback_query(lambda c: c.data.startswith("trans:"))
async def select_transport(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    mapping = {"car":"На машине","taxi":"На такси","horse":"На коне"}
    text = mapping.get(key)
    await callback.message.edit_reply_markup()
    if key == "car":
        await callback.message.answer("✅ Отлично, там есть парковочные места прямо рядом с рестораном.")
    else:
        await callback.message.answer(f"✅ Вы выбрали: {text}")
    await state.update_data(transport=text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💃 Да, очень люблю танцевать", callback_data="dance:yes")],
        [InlineKeyboardButton(text="🕺 Может быть потанцую немного", callback_data="dance:maybe")],
        [InlineKeyboardButton(text="👀 Я просто посмотрю, как танцуют другие", callback_data="dance:no")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back:transport")]
    ])
    await callback.message.answer("🕺 Будете ли вы танцевать?", reply_markup=keyboard)
    await state.set_state(Form.dance)

# dance
@dp.callback_query(lambda c: c.data.startswith("dance:"))
async def select_dance(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split(":")[1]
    mapping = {"yes":"Да, очень люблю танцевать","maybe":"Может быть потанцую","no":"Просто посмотрю"}
    text = mapping.get(key)
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"✅ Вы выбрали: {text}")
    await state.update_data(dance=text)

    # итог
    data = await state.get_data()
    summary = (
        f"📨 <b>Новое подтверждение:</b>\n"
        f"👤 Имя: {data['name']}\n"
        f"🍽 Блюдо: {data['main_course']}\n"
        f"🍷 Алкоголь: {data['alcohol']}\n"
        f"🎭 Активности: {data['activities']}\n"
        f"🚙 Транспорт: {data['transport']}\n"
        f"🕺 Танцы: {data['dance']}"
    )
    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=summary, parse_mode=ParseMode.HTML)
        except Exception as e:
            await callback.message.answer(f"Ошибка отправки админу: {e}")
    await callback.message.answer("🎉 Спасибо! Присоединяйся к свадебному чату: https://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
