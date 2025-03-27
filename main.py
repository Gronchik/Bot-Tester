from datetime import timedelta

import segno
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from qrcode.main import QRCode

from handlers import create_test, start, pagination
from DataBase.DAO import DAO
from bot_classes import *
import asyncio
from segno import helpers

from handlers.pagination import create_pagination

logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования
bot = Bot()  # Создаём класс бота
dp = Dispatcher()  # Создаём диспетчер
dp.include_routers(create_test.router, start.router, pagination.router)  # Присоединяем все роутеры

@dp.callback_query(F.data.startswith('callba') or F.data == "back")
async def f(calb:CallbackQuery):
    print(calb.data)

@dp.message(CommandStart())
async def reg(msg: Message, state: FSMContext):
    data = await create_pagination(state, ["ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe"],
                            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14,15,16,17,18,19,20,21], "callba",
                                   "back")
    print(data)
    await msg.answer(data[0], reply_markup=data[1])

async def main():
    print(datetime.now() + timedelta(hours=1))
    await dp.start_polling(bot)  # Начинаем приём сообщений


asyncio.run(main())
