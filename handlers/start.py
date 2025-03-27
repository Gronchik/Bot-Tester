from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from DataBase.DAO import DAO
from bot_classes import *

router = Router()

class GetName(StatesGroup):
    name = State()
    test_id = int


@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    print("ergg")
    if not DAO.User.check_user(msg.from_user.id):
        await state.set_state(GetName.name)
        await msg.answer("⬇️Введите ваше имя⬇️")  #todo занос в стейт теста и тд
        await msg.delete()

@router.message(GetName.name)
async def get_name(msg: Message, state: FSMContext):
    user = User(msg.from_user.id, msg.chat.id, msg.from_user.username, msg.text)
    DAO.User.add_user(user)
    await msg.answer(f"Вы были успешно зарегистрированы под именем: {msg.text}\nИзменить имя можно в настройках")
