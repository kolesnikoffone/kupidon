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
    activities = State()

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
            "Привет! Я Купидончик 💘\n"
            "Готов(а) ответить на пару вопросов, чтобы подтвердить участие в свадьбе?"
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать", callback_data="start_form")],
            [InlineKeyboardButton(
                text="📅 Добавить в календарь",
                url="https://www.google.com/calendar/render?action=TEMPLATE&text=Свадьба+Игоря+и+Анастасии&dates=20250723T120000/20250723T160000&ctz=Europe/Moscow&details=Регистрация:+https://yandex.ru/maps/-/CHrU5XZ4+%0AБанкет:+https://yandex.ru/maps/-/CHrUBE2i+%0AДресс-код:+классика+в+пастельных+тонах&location=Екатерининский+зал,+Двин+Холл"
            )]
        ])
    )

@dp.callback_query(lambda c: c.data == "start_form")
async def handle_start_form(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📅 Добавить в календарь",
            url="https://www.google.com/calendar/render?action=TEMPLATE&text=Свадьба+Игоря+и+Анастасии&dates=20250723T120000/20250723T160000&ctz=Europe/Moscow&details=Регистрация:+https://yandex.ru/maps/-/CHrU5XZ4+%0AБанкет:+https://yandex.ru/maps/-/CHrUBE2i+%0AДресс-код:+классика+в+пастельных+тонах&location=Екатерининский+зал,+Двин+Холл"
        )]
    ]))
    await callback.message.answer("👤 Как тебя зовут? (Имя и Фамилия)")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐟 Рыба", callback_data="food:Рыба")],
        [InlineKeyboardButton(text="🥩 Мясо", callback_data="food:Мясо")],
        [InlineKeyboardButton(text="🍗 Курица", callback_data="food:Курица")],
        [InlineKeyboardButton(text="🥦 Овощи и грибы", callback_data="food:Овощи и грибы")]
    ])
    await message.answer("🍽 Что вы предпочитаете в качестве основного блюда?", reply_markup=keyboard)
    await state.set_state(Form.main_course)

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
        [InlineKeyboardButton(text="📝 Пропустить", callback_data="alc:Пропустить")]
    ])
    await callback.message.answer("🍷 Предпочтения по алкоголю:", reply_markup=keyboard)
    await state.set_state(Form.alcohol)

@dp.callback_query(lambda c: c.data.startswith("alc:"))
async def select_alcohol(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"✅ Вы выбрали: {choice}")
    await state.update_data(alcohol=choice)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎉 Да, очень хочу!", callback_data="act:yes")],
        [InlineKeyboardButton(text="🤔 Может быть", callback_data="act:maybe")],
        [InlineKeyboardButton(text="🍽 Оставьте меня в покое, я хочу покушать", callback_data="act:no")]
    ])
    await callback.message.answer("🎭 Хотите ли вы участвовать в активностях от ведущего?", reply_markup=keyboard)
    await state.set_state(Form.activities)

    data = await state.get_data()
    summary = (
        f"📨 Новое подтверждение:
"
        f"👤 Имя: {data.get('name')}
"
        f"🍽 Блюдо: {data.get('main_course')}
"
        f"🍷 Алкоголь: {data.get('alcohol')}
"
        f"🎭 Активности: {data.get('activities')}"
    )}\n"
        f"🍽 Блюдо: {data.get('main_course')}\n"
        f"🍷 Алкоголь: {data.get('alcohol')}"
    )

    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=summary)
        except Exception as e:
            await callback.message.answer(f"Ошибка отправки админу: {e}")

    await callback.message.answer("🎉 Спасибо! Присоединяйся к свадебному чату: https://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith("act:"))
async def select_activities(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split(":")[1]
    text = {
        "yes": "🎉 Да, очень хочу!",
        "maybe": "🤔 Может быть",
        "no": "🍽 Оставьте меня в покое, я хочу покушать"
    }.get(choice, choice)
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"✅ Вы выбрали: {text}")
    await state.update_data(activities=text)

    data = await state.get_data()
    summary = (
        f"📨 Новое подтверждение:
"
        f"👤 Имя: {data.get('name')}
"
        f"🍽 Блюдо: {data.get('main_course')}
"
        f"🍷 Алкоголь: {data.get('alcohol')}
"
        f"🎭 Активности: {data.get('activities')}"
    )

    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=summary)
        except Exception as e:
            await callback.message.answer(f"Ошибка отправки админу: {e}")

    await callback.message.answer("🎉 Спасибо! Присоединяйся к свадебному чату: https://t.me/+T300ZeTouJ5kYjIy")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
