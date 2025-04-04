import asyncio
from random import randint

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Text, Bold, Pre, Italic

from DataBase.DAO import DAO
from bot_classes import *
from inline_keyboards.start_test import get_test_keyb_one_answ, get_test_keyb_many_answ, get_accept_keyb

router = Router()

class Testing(StatesGroup):
    answer = State()
    super_test = SuperTest
    test_id = 0
    answers = list[UserTestAnswer]

def shift_right(arr, n):
    """Функция сдвигает индексы списка на n позиций"""
    n = n % len(arr)  # Учитываем случай, когда n > длины массива
    return arr[-n:] + arr[:-n]

def test_to_str(test: Test, num: int) -> str:
    text = Pre(test.text, language=f"Вопрос_{num}")
    return text.as_markdown()

async def save_data_end_edit_msg(state: FSMContext, new_state, bot: Bot, data, chat_id: int, text: str,
                                 keyboard = None):
    """Функция удаляет старое сообщение, отправляет новое, заносит его id в data, и изменяет стейт пользователя"""
    await bot.delete_message(chat_id, data['start_test_msg_id'])
    bot_msg = await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
    data['start_test_msg_id'] = bot_msg.message_id
    await state.set_state(new_state)
    await state.set_data(data)

@router.callback_query(F.data.startswith('start_super_test_'))
async def start_test(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    await state.clear()
    stest_id = calb.data.split('_')[3]
    super_test = DAO.SuperTest.get_for_id(stest_id)

    data = {'super_test': super_test,
            'test_num': 0,
            'answers': [],
            'shifts': [randint(0, 16) for i in range(len(super_test.tests_id))],
            'test_msg_id': int}

    test: Test = DAO.Test.get(data['super_test'].tests_id[data['test_num']])
    data['test'] = test
    text = test_to_str(test, data['test_num'] + 1)
    keyb = get_test_keyb_many_answ(test, [], data['shifts'][0])

    if test.type == TestType.FreeAnswerQuiz:
        await state.set_state(Testing.answer)

    new_msg = await msg.edit_text(text, reply_markup=keyb, parse_mode=ParseMode.MARKDOWN_V2)
    data['test_msg_id'] = new_msg.message_id
    await state.set_data(data)

@router.callback_query(F.data.startswith('test_answer_'))
async def test_answer(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    data = await state.get_data()
    answer_id = int(calb.data.split('_')[2])
    super_test: SuperTest = data['super_test']
    test: Test = data['test']
    answers: list[UserTestAnswer] = data['answers']

    #  Если на настоящий тест даётся только один вариант ответа, то принимаем его и переходим к следующему вопросу
    if test.count_of_correct == 1 and test.type == TestType.Quiz:
        ltest_num = data['test_num']
        if len(super_test.tests_id) > data['test_num'] + 1:
            data['test_num'] += 1
        else:
            await calb.answer("Вопросы закончились")

        for answer in answers:
            if answer.test_id == test.id:
                answers.remove(answer)
                break

        answers.append(UserTestAnswer(super_test.tests_id[ltest_num], [int(answer_id)], test))
        new_test = DAO.Test.get(super_test.tests_id[data['test_num']])
        selected = []
        #  Заносим в выбранные те ответы, которые были даны на этот тест, если такие были
        for answer in answers:
            if answer.test_id == new_test.id:
                selected.append(*answer.answer)
                break

        data['test'] = new_test
        text = test_to_str(new_test, data['test_num'] + 1)

        keyb = get_test_keyb_many_answ(new_test, selected, data['shifts'][data['test_num']])

        if test.type == TestType.FreeAnswerQuiz:
            await state.set_state(Testing.answer)
            text += "\n" + Pre(*selected, language="Ответ").as_markdown()

        await state.set_data(data)
        await msg.edit_text(text, reply_markup=keyb, parse_mode=ParseMode.MARKDOWN_V2)

    elif test.count_of_correct > 1 and test.type == TestType.Quiz:
        answer_now = []
        for i in answers:
            if i.test_id == test.id:
                answer_now = i.answer
                answers.remove(i)
                break

        if answer_id in answer_now:
            answer_now.remove(answer_id)
            answers.append(UserTestAnswer(super_test.tests_id[data['test_num']], answer_now, test))
        else:
            answers.append(UserTestAnswer(super_test.tests_id[data['test_num']], [int(answer_id)] + answer_now, test))

        selected = []
        #  Заносим в выбранные те ответы, которые были даны на этот тест, если такие были
        for answer in answers:
            if answer.test_id == test.id:
                selected += answer.answer
                break

        text = test_to_str(test, data['test_num'] + 1)

        keyb = get_test_keyb_many_answ(test, selected, data['shifts'][data['test_num']])

        await state.set_data(data)
        await msg.edit_text(text, reply_markup=keyb, parse_mode=ParseMode.MARKDOWN_V2)

@router.callback_query(lambda calb: calb.data in ['last_test', 'next_test'])
async def swipe_test(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    data = await state.get_data()
    super_test: SuperTest = data['super_test']
    answers = data['answers']

    if calb.data == 'last_test' and data['test_num'] - 1 >= 0:
        data['test_num'] -= 1
    elif calb.data == 'next_test' and data['test_num'] + 1 < len(super_test.tests_id):
        data['test_num'] += 1
    else:
        await calb.answer("Тесты закончились")

    new_test = DAO.Test.get(super_test.tests_id[data['test_num']])
    selected = []
    #  Заносим в выбранные те ответы, которые были даны на этот тест, если такие были
    for answer in answers:
        if answer.test_id == new_test.id:
            selected += answer.answer
            break

    data['test'] = new_test
    text = test_to_str(new_test, data['test_num'] + 1)

    keyb = get_test_keyb_many_answ(new_test, selected, data['shifts'][data['test_num']])

    if new_test.type == TestType.FreeAnswerQuiz:
        await state.set_state(Testing.answer)
        text += "\n" + Pre(*selected, language="Ответ").as_markdown()
    else:
        await state.set_state(None)

    await state.set_data(data)
    await msg.edit_text(text, reply_markup=keyb, parse_mode=ParseMode.MARKDOWN_V2)

@router.message(Testing.answer)
async def msg_answer(msg: Message, state: FSMContext, bot: Bot):
    """"""
    data = await state.get_data()
    super_test: SuperTest = data['super_test']
    answers: list[UserTestAnswer] = data['answers']
    test: Test = data['test']

    for answer in answers:
        if answer.test_id == test.id:
            answers.remove(answer)
            break

    answers.append(UserTestAnswer(super_test.tests_id[data['test_num']], [msg.text], test))
    text = test_to_str(test, data['test_num'] + 1)
    text += "\n" + Pre(msg.text, language="Ответ").as_markdown()

    keyb = get_test_keyb_many_answ(test, [], data['shifts'][data['test_num']])

    await state.set_data(data)
    await bot.edit_message_text(text, chat_id=msg.chat.id, message_id=data['test_msg_id'], reply_markup=keyb,
                                parse_mode=ParseMode.MARKDOWN_V2)
    await msg.delete()

@router.callback_query(F.data == 'return_test')
async def return_test(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    data = await state.get_data()
    super_test: SuperTest = data['super_test']
    answers: list[UserTestAnswer] = data['answers']

    new_test = DAO.Test.get(super_test.tests_id[data['test_num']])
    selected = []
    #  Заносим в выбранные те ответы, которые были даны на этот тест, если такие были
    for answer in answers:
        if answer.test_id == new_test.id:
            selected += answer.answer
            break

    data['test'] = new_test
    text = test_to_str(new_test, data['test_num'] + 1)

    keyb = get_test_keyb_many_answ(new_test, selected, data['shifts'][data['test_num']])

    if new_test.type == TestType.FreeAnswerQuiz:
        await state.set_state(Testing.answer)
        text += "\n" + Pre(*selected, language="Ответ").as_markdown()
    else:
        await state.set_state(None)

    await state.set_data(data)
    await msg.edit_text(text, reply_markup=keyb, parse_mode=ParseMode.MARKDOWN_V2)


@router.callback_query(F.data == 'confirm_end_test')
async def swipe_test(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    await state.set_state(None)
    await msg.edit_text("Вы уверены, что хотите закончить прохождение теста?", reply_markup=get_accept_keyb())

@router.callback_query(F.data == 'finish_test')
async def finish_test(calb: CallbackQuery, state: FSMContext):
    msg = calb.message
    data = await state.get_data()

    super_test: SuperTest = data['super_test']
    answers: list[UserTestAnswer] = data['answers']
    points = 0

    answers_sort_int = []
    answers_int = [i.answer for i in answers]
    tests_int = [i.test_id for i in answers]
    for i in super_test.tests_id:
        try:
            idd = tests_int.index(i)
            answers_sort_int.append(answers_int[idd])
        except ValueError:
            answers_sort_int.append([999])

    for answer in answers:
        points += answer.result

    result = round(points / len(super_test.tests_id), 2) * 100

    progressbar = "🟩" * int(result / 10) + "⬜️" * (10 - int(result / 10))
    text = Text(Bold(f'Результаты: {points}/{len(super_test.tests_id)}\n'),
                progressbar, " ",  int(result), "%").as_markdown()
    DAO.Answer.add(UserSuperTestAnswer(None, calb.from_user.id, super_test.id, answers_sort_int, result))
    await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)
