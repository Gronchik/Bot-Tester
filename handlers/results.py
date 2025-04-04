from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from DataBase.DAO import DAO
from bot_classes import *
from handlers.create_test import poosh_msg
from handlers.pagination import create_pagination
from datetime import datetime
from aiogram.utils.formatting import Text, Bold, Code
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openpyxl import Workbook
from io import BytesIO

router = Router()

class ResultsState(StatesGroup):
    ChoosingTestType = State()
    ViewingCreated = State()
    ViewingCompleted = State()

@router.message(Command("results"))
async def handle_results(msg: Message, state: FSMContext, bot: Bot):
    if int(msg.from_user.id) != int(bot.id):
        user_id = msg.from_user.id
    else:
        user_id = msg.chat.id

    created_tests = DAO.SuperTest.get_for_user(user_id)
    completed_answers = DAO.Answer.get_for_user(user_id)

    # Фильтрация уникальных пройденных тестов по answer_id
    completed_tests = {answer.id: answer for answer in completed_answers if answer.stest_id}

    if not created_tests and not completed_tests:
        await poosh_msg(msg, "У вас нет созданных или пройденных тестов")
        return

    await state.update_data(created=created_tests, completed=completed_tests)

    if created_tests and completed_tests:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Мои тесты", callback_data="res_type_created")],
            [InlineKeyboardButton(text="Пройденные тесты", callback_data="res_type_completed")]
        ])

        if msg.from_user.id == bot.id:
            await msg.edit_text("Выберите тип тестов для просмотра:", reply_markup=keyboard)
        else:
            await msg.answer("Выберите тип тестов для просмотра:", reply_markup=keyboard)
        await state.set_state(ResultsState.ChoosingTestType)
    else:
        data_type = "created" if created_tests else "completed"
        tests = list(created_tests) if created_tests else list(completed_tests.values())
        await show_tests_list(msg, tests, data_type, state, user_id, bot)


@router.callback_query(F.data.startswith("res_type_"))
async def handle_test_type_choice(callback: CallbackQuery, state: FSMContext, bot: Bot):
    test_type = callback.data.split("_")[2]
    data = await state.get_data()

    tests = data.get("created", []) if test_type == "created" else data.get("completed", {}).values()

    await callback.message.delete()

    await show_tests_list(callback.message, tests, test_type, state, callback.from_user.id, bot)
    await state.set_state(ResultsState.ViewingCreated if test_type == "created" else ResultsState.ViewingCompleted)


@router.callback_query(F.data == "res_back")
async def handle_back(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if await state.get_state() in [ResultsState.ViewingCreated, ResultsState.ViewingCompleted]:
        # Возврат к выбору типа тестов
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Мои тесты", callback_data="res_type_created")],
            [InlineKeyboardButton(text="Пройденные тесты", callback_data="res_type_completed")]
        ])
        await callback.message.edit_text("Выберите тип тестов для просмотра:", reply_markup=keyboard)
        await state.set_state(ResultsState.ChoosingTestType)
    else:
        await handle_results(callback.message, state, bot)
        await callback.answer()

async def show_tests_list(msg: Message, tests: list, test_type: str, state: FSMContext, user_id, bot: Bot):
    if not tests:
        await msg.answer("По выбранному типу тестов не найдено")
        return

    texts = []
    indexes = []

    if test_type == "created":
        for test in tests:
            texts.append(f"{test.name}")
            indexes.append(test.id)
    else:
        answers = DAO.Answer.get_for_user(user_id)

        for answer in answers:
            stest = DAO.SuperTest.get_for_id(answer.stest_id)
            text = f"{stest.name}" if stest else "Удаленный тест"
            texts.append(text)
            indexes.append(answer.id)

        print(texts, indexes)

    text, keyb = await create_pagination(
        state=state,
        texts=texts,
        indexes=indexes,
        callback=f"res_{test_type}_",
        back_callback="res_back",
        items_on_page=5
    )
    if msg.from_user.id == bot.id:
        try: await msg.edit_text(
            f"Список {'созданных' if test_type == 'created' else 'пройденных'} тестов:\n{text}",
            reply_markup=keyb
        )
        except: print("Ощибка")
    else:
        await msg.answer(
            f"Список {'созданных' if test_type == 'created' else 'пройденных'} тестов:\n{text}",
            reply_markup=keyb
        )
    await state.update_data(current_type=test_type)


@router.callback_query(F.data.startswith("res_completed_"))
async def handle_completed_answer_selection(callback: CallbackQuery, state: FSMContext):
    answer_id = int(callback.data.split("_")[2])

    answer = DAO.Answer.get_for_id(answer_id)
    if not answer or not answer.answers:
        await callback.answer("Данные ответа не найдены")
        return

    super_test = DAO.SuperTest.get_for_id(answer.stest_id)
    if not super_test:
        await callback.answer("Тест удален")
        return

    response = [f"Результаты теста: {super_test.name}"]

    for test_id in super_test.tests_id:
        test = DAO.Test.get(test_id)
        answ = answer.answers[super_test.tests_id.index(test_id)]
        answ_text = []
        for i in answ:
            try:
                if int(i) == 999:
                    answ_text.append('-')
                    continue
                answ_text.append(test.variants[int(i)])
            except (ValueError, IndexError):
                answ_text.append(i)

        text = (f"\nВопрос: {test.text}\n"
                f"Ответ: {', '.join(answ_text)}")
        response.append(text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="res_back")]
    ])

    full_text = "\n".join(response)
    if len(full_text) > 4000:
        parts = [full_text[i:i + 4000] for i in range(0, len(full_text), 4000)]
        for part in parts:
            await callback.message.answer(part)
        await callback.message.answer("⬆ Результаты теста", reply_markup=keyboard)
    else:
        await callback.message.edit_text(full_text, reply_markup=keyboard)

    await callback.answer()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="res_back")]
    ])

    full_text = "\n".join(response)
    # ... обработка длинных сообщений ...


@router.callback_query(F.data.startswith("res_created_"))
async def handle_created_test_selection(callback: CallbackQuery):
    test_id = int(callback.data.split("_")[2])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Excel", callback_data=f"export_excel_{test_id}")],
        [InlineKeyboardButton(text="Текст", callback_data=f"export_txt_{test_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="res_back")]
    ])
    await callback.message.edit_text("📤 Выберите формат экспорта:", reply_markup=keyboard)

@router.callback_query(F.data.startswith('export_txt_'))
async def export_txt(calb: CallbackQuery):
    stest_id = int(calb.data.split("_")[2])
    results = DAO.Answer.get_detailed_answers(stest_id)
    super_test = DAO.SuperTest.get_for_id(stest_id)

    text = Text(
        Bold(f"Результаты теста: {super_test.name}\n"),
        f"Всего участников: {len(results)}\n\n"
    ).as_markdown()

    # Сортируем по убыванию баллов
    results_sorted = sorted(results, key=lambda x: x['total_score'], reverse=True)[:10]

    for i, res in enumerate(results_sorted, 1):
        user_text = Text(f"{i}. {res['name']} (@{res['username']})\n")

        for answer in res['answers']:
            user_text += Text(
                f"Вопрос: {answer['question']}\n"
                f"Ответ: {answer['answers']}\n"
            )

        user_text += Text(f"Всего баллов: {res['total_score']}\n\n")
        text += user_text.as_markdown()
    await calb.message.edit_text(text,
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="res_back")]]),
                                 parse_mode=ParseMode.MARKDOWN_V2)

@router.callback_query(F.data == "res_back")
async def handle_back(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    test_type = data["current_type"]

    if test_type:
        print(1)
        tests = data["created"] if test_type == "created" else data["completed"].values()
        await callback.message.delete()
        await show_tests_list(callback.message, tests, test_type, state, callback.from_user.id, bot)
    else:
        print(2)
        await handle_results(callback.message, state, bot)


@router.callback_query(F.data == "res_back_type")
async def handle_back_type(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await handle_results(callback.message, state, bot)