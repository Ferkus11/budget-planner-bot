from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from db import init_db, add_record, delete_last_expense, delete_category, get_statistics, get_income_statistics
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # лог в файл
        logging.StreamHandler()  # лог в консоль
    ]
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
init_db()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить трату"), KeyboardButton(text="💰 Доход")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🗑 Удалить последнюю"), KeyboardButton(text="🧹 Удалить категорию")]
    ],
    resize_keyboard=True
)

user_states = {}



@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу тебе вести бюджет 💰", reply_markup=main_keyboard)


@dp.message(lambda m: m.text == "📊 Статистика")
async def stats_handler(message: Message):
    user_id = message.from_user.id
    expenses = get_statistics(user_id)
    incomes = get_income_statistics(user_id)

    if not expenses and not incomes:
        await message.answer("У тебя пока нет ни доходов, ни расходов 💸")
        return

    text = ""

    if expenses:
        text += "<b>💸 Расходы по категориям:</b>\n"
        for cat, total in expenses:
            text += f"• {cat}: {total}₽\n"

    if incomes:
        text += "\n<b>💰 Доходы по категориям:</b>\n"
        for cat, total in incomes:
            text += f"• {cat}: {total}₽\n"

    await message.answer(text)

@dp.message(lambda m: m.text == "🗑 Удалить последнюю")
async def delete_last_handler(message: Message):
    delete_last_expense(message.from_user.id)
    await message.answer("Удалена последняя запись.")

@dp.message(lambda m: m.text == "🧹 Удалить категорию")
async def delete_category_prompt(message: Message):
    user_states[message.from_user.id] = "awaiting_category_delete"
    await message.answer("Введи название категории, которую хочешь удалить:")

@dp.message(lambda m: m.text == "💰 Доход")
async def handle_income_prompt(message: Message):
    await message.answer(
        "Введи доход в формате: &lt;категория&gt; &lt;сумма&gt;\nПример: зарплата 1000"
    )

@dp.message(lambda m: m.text == "➕ Добавить трату")
async def handle_add_expense_prompt(message: Message):
    await message.answer(
        "Введи трату в формате: &lt;категория&gt; &lt;сумма&gt;\nПример: еда 200"
    )


@dp.message()
async def generic_handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip().lower()
    if user_states.get(user_id) == "awaiting_category_delete":
        delete_category(user_id, text)
        await message.answer(f"✅ Категория <b>{text}</b> удалена.")
        user_states.pop(user_id)
        return
    try:
        parts = message.text.split()
        if len(parts) == 2:
            category = parts[0]
            amount = int(parts[1])

            if category in ["зарплата", "доход"]:
                add_record(user_id, category, amount, record_type="income")
                await message.answer(f"💰 Доход {category} {amount}₽ добавлен.")
            else:
                add_record(user_id, category, amount)
                await message.answer(f"💸 Трата {category} {amount}₽ добавлена.")
        else:
            await message.answer("Непонятный ввод. Пример: еда 200")
    except ValueError:
        await message.answer("Сумма должна быть целым числом.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

