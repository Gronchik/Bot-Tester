from aiogram import Router, types, F, Bot
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Text, Code
from DataBase.DAO import DAO
from bot_classes import *
from inline_keyboards.start_test import get_start_stest_keyb

router = Router()

class GetName(StatesGroup):
    name = State()
    test_id = int

def stest_to_str(super_test: SuperTest) -> str:
    descr = ['\nОписание: ', Code(super_test.description)]
    return Text(f"Тест: ", Code(super_test.name),
                *descr if super_test.description is not None else '',
                f"\nКол-во вопросов: ", Code(str(len(super_test.tests_id))),
                f"\nДата окончания теста: ", Code(super_test.end_date.strftime('%Y.%m.%d %H:%M'))).as_markdown()

@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    data = await state.get_data()
    args = msg.text.split()

    if len(args) == 2:
        data['start_test_id'] = deconvert_stest_id(args[1])

    if not DAO.User.check_user(msg.from_user.id):
        await state.set_state(GetName.name)
        await msg.answer("Введите ваше имя")
    elif len(args) == 2:
        super_test = DAO.SuperTest.get_for_id(deconvert_stest_id(args[1]))
        #  Обработка случая не нахождения теста
        if super_test is None:
            await msg.answer('Тест не найден')
        else:
            await msg.answer(stest_to_str(super_test), reply_markup=get_start_stest_keyb(super_test.id), parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await msg.answer("Вы уже зарегистрированы в боте")
    await msg.delete()

@router.message(GetName.name)
async def get_name(msg: Message, state: FSMContext):
    user = User(msg.from_user.id, msg.chat.id, msg.from_user.username, msg.text)
    data = await state.get_data()
    DAO.User.add_user(user)
    await msg.answer(f"Вы были успешно зарегистрированы под именем: {msg.text}\nИзменить имя можно в настройках",
                     parse_mode=ParseMode.MARKDOWN_V2)

    if 'start_test_id' in data.keys:
        super_test = DAO.SuperTest.get_for_id(data['start_test_id'])
        if super_test is None:
            await msg.answer('Тест не найден')
        else:
            text = stest_to_str(super_test)
            await msg.answer(text, reply_markup=get_start_stest_keyb(super_test.id))


