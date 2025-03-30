from datetime import timedelta

import segno
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from qrcode.main import QRCode

from handlers import create_test, start, pagination, start_test
from DataBase.DAO import DAO
from bot_classes import *
import asyncio
from segno import helpers

from handlers.create_test import get_super_test_in_str, get_test_in_str
from handlers.pagination import create_pagination

logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования
bot = Bot(token=r"")  # Создаём класс бота
dp = Dispatcher()  # Создаём диспетчер
dp.include_routers(create_test.router, start.router, pagination.router, start_test.router)  # Присоединяем все роутеры

#@dp.callback_query()
async def f(calb:CallbackQuery):
    print(calb.data)

#@dp.message(CommandStart())
async def reg(msg: Message, state: FSMContext):
    data = await create_pagination(state, ["ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe", "ergrg", "sggerg", "wegfwe"],
                            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14,15,16,17,18,19,20,21], "callba",
                                   "back")
    print(data)
    await msg.answer(data[0], reply_markup=data[1])
    pass

async def main():
    print()
    print(datetime.now() + timedelta(hours=1))
    await dp.start_polling(bot, skip_updates=True)  # Начинаем приём сообщений


asyncio.run(main())
