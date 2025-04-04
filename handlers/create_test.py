import asyncio
from datetime import timedelta

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, BufferedInputFile
from aiogram.utils.formatting import Text, Code
from DataBase.DAO import DAO
from bot_classes import *
from handlers.pagination import create_pagination
from inline_keyboards.create_test import get_cancel_keyb, get_skip_keyb, get_access_descr_stest_keyb, \
    get_cancel_edit_keyb, get_test_types_keyb, get_skip_test_name_keyb, get_final_test_keyb, get_cancel_edit_test, \
    get_question_create_test, get_create_stest_keyb, get_del_or_accept_test_keyb, get_test_selection, \
    get_final_test_keyb_v2

router = Router(name="CreatingTestModule")


class Get(StatesGroup):
    TestName = State()
    TestDescr = State()
    TestAnswers = State()
    TestCountCorrect = State()
    TestDate = State()
    TestEditName = State()
    TestEditDescr = State()
    TestEditAnswers = State()
    EditTestName = State()
    EditTestDescr = State()
    SuperTestName = State()
    SuperTestDescr = State()
    EditSuperTestName = State()
    EditSuperTestDescr = State()
    EditSuperTestDate = State()


async def save_data_end_edit_msg(state: FSMContext, new_state, bot: Bot, data, chat_id: int, text: str,
                                 keyboard: InlineKeyboardMarkup = None):
    """Функция удаляет старое сообщение, отправляет новое, заносит его id в data, и изменяет стейт пользователя"""
    await bot.delete_message(chat_id, data['create_test_msg_id'])
    bot_msg = await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
    data['create_test_msg_id'] = bot_msg.message_id
    await state.set_state(new_state)
    await state.set_data(data)


async def poosh_msg(msg: Message, text: str, not_del = False):
    """Функция выводит пуш-сообщение на 5 секунд и удаляет его"""
    if not not_del:
        await msg.delete()
    bot_msg = await msg.answer(text)
    await asyncio.sleep(5)
    await bot_msg.delete()


def get_test_in_str(test: Test) -> str:
    """Функция создаёт текст сообщения с параметрами теста"""
    # Добавляем правильные и не правильные варианты ответа, если тип теста Quiz, если FreeAnswerQuiz, то
    # выводим все ответы, как правильные
    strs = []
    if test.type == TestType.Quiz:
        for correct in test.variants[0:test.count_of_correct]:
            strs.append(Code(correct + ' '))
        strs.append("\nНеверные ответы: ")
        for wrong in test.variants[test.count_of_correct:]:
            strs.append(Code(wrong + ' '))
    elif test.type == TestType.FreeAnswerQuiz:
        strs.append(Code(', '.join(test.variants)))

    text = Text(f"Название: ", Code(test.name),
                f"\nТекст: ", Code(test.text),
                f"\nВерные ответы: ", *strs)

    return text.as_markdown()


def get_super_test_in_str(super_test: SuperTest, finall_str="Выберите что изменить, или подтвердите создание") -> str:
    """Функция создаёт текст сообщения с параметрами супер-теста"""
    str_date = super_test.end_date.strftime("%d.%m.%Y %H:%M")
    description = 'Отсутствует' if super_test.description == '' else  Code(super_test.description)
    tests_str = []
    # Если супер-тесту присвоены тесты, добавляем их названия
    if len(super_test.tests_id) > 0:
        tests = DAO.Test.multiple_get(super_test.tests_id)
        tests_str.append(f"\nВопросы:")
        counter = 0
        for test in tests:
            counter += 1
            tests_str.append(f"\n{counter}) ")
            tests_str.append(Code(test.text))
    text = Text(f"Название теста: ", Code(super_test.name),
                f"\nОписание теста: ", description,
                f"\nДата окончания: ", Code(str_date),
                *tests_str)
    return text.as_markdown()


@router.message(Command("create_test"))
async def create_super_test(msg: Message, state: FSMContext):
    """Функция начинает создание супер-теста и направляет на введение названия"""
    new_msg = await msg.answer("Введите название теста", reply_markup=get_cancel_keyb())
    await state.set_state(Get.SuperTestName)
    await state.update_data(create_test_msg_id=new_msg.message_id)


@router.message(Get.SuperTestName)
async def get_super_test_name(msg: Message, state: FSMContext, bot: Bot):
    """Функция получает название теста, заносит объект супер-теста в data стейта пользователя и направляет на введение описания"""
    data = await state.get_data()
    super_test = SuperTest(None, [], msg.from_user.id, None, None, msg.text)
    data['new_super_test'] = super_test
    await save_data_end_edit_msg(state, Get.SuperTestDescr, bot, data, msg.chat.id, "Введите описание теста",
                                 get_skip_keyb())
    await msg.delete()


@router.message(Get.SuperTestDescr)
async def get_super_test_description(msg: Message, state: FSMContext, bot: Bot):
    """Функция получает и заносит в data пользователя описание и выводит меню с информацией о супер-тесте, и просит подтвердить или изменить"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    super_test.description = msg.text
    await save_data_end_edit_msg(state, Get.TestDate, bot, data, msg.chat.id,
                                 f"Введите дату и время в формате: \nдень:месяц:год:часы:минуты\n"
                                 f"Пример: 04:03:2025:16:42 —\\> \n"
                                 f"4 марта 2025 года, 16:42")
    await msg.delete()


@router.callback_query(F.data == "description_skip")
async def skip_description(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция пропускает ввод описание и присваивает ему значение пустой строки и возвращает меню подтверждения супер-теста"""
    msg = calb.message
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    super_test.description = ""
    await save_data_end_edit_msg(state, Get.TestDate, bot, data, msg.chat.id,
                                 f"Введите дату и время в формате: день:месяц:год:часы:минуты\n"
                                 f"Пример: 04:03:2025:16:42 —\\> \n"
                                 f"4 марта 2025 года, 16:42")


@router.message(Get.TestDate)
async def input_end_date(msg: Message, state: FSMContext, bot: Bot):
    """Функция получает дату от пользователя и сохраняет её"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']

    try:
        super_test.end_date = datetime.strptime(msg.text, "%d:%m:%Y:%H:%M")
        if super_test.end_date is None: raise ValueError
    except ValueError:
        await poosh_msg(msg, "Некорректная дата")
        return

    if super_test.end_date <= datetime.now() + timedelta(hours=1):
        await poosh_msg(msg, "Время конца должно быть минимум на час больше, чем настоящее")
    else:

        if len(super_test.tests_id) == 0:
            keyb = get_access_descr_stest_keyb()
        else:
            keyb = get_create_stest_keyb()

        text = get_super_test_in_str(super_test)
        await save_data_end_edit_msg(state, None, bot, data, msg.chat.id, text, keyb)
        await msg.delete()


@router.callback_query(F.data == "edit_name")
async def edit_name(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция принимает новое название супер-теста при его изменении во время создания"""
    data = await state.get_data()
    await save_data_end_edit_msg(state, Get.EditSuperTestName, bot, data, calb.message.chat.id, "Введите название",
                                 get_cancel_edit_keyb())


@router.callback_query(F.data == "edit_description")
async def edit_description(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция направляет на введение нового названия супер-теста при его создании"""
    msg = calb.message
    data = await state.get_data()
    await save_data_end_edit_msg(state, Get.EditSuperTestDescr, bot, data, msg.chat.id, "Введите описание",
                                 get_cancel_edit_keyb())


@router.callback_query(F.data == "edit_end_date")
async def edit_end_date(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция направляет на введение новой даты окончания супер-теста при его создании"""
    data = await state.get_data()
    text = Text(f"Введите дату и время окончания теста в формате: день:месяц:год:часы:минуты\n"
                                 f"Пример: 04:03:2025:16:42 —> \n"
                                 f"4 марта 2025 года, 16:42").as_markdown()
    await save_data_end_edit_msg(state, Get.TestDate, bot, data, calb.message.chat.id, text, get_cancel_edit_keyb())


@router.message(StateFilter(Get.EditSuperTestName, Get.EditSuperTestDescr))
async def edit_descr_or_name(msg: Message, state: FSMContext, bot: Bot):
    """Функция принимает новое название либо описание и присваивает его супер-тесту при его создании и возвращает меню
       подтверждения супер-теста"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']

    # Проверка того, что изменяем по стейту пользователя
    if (await state.get_state()) == Get.EditSuperTestDescr:
        super_test.description = msg.text
    else:
        super_test.name = msg.text

    if len(super_test.tests_id) == 0:
        keyb = get_access_descr_stest_keyb()
    else:
        keyb = get_create_stest_keyb()
    text = get_super_test_in_str(super_test)

    await save_data_end_edit_msg(state, None, bot, data, msg.chat.id, text, keyb)
    await msg.delete()


@router.callback_query(F.data == "cancel_edit")
async def cancel_edit_super_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция отмены изменения названия или описания супер-теста при его создании"""
    msg = calb.message
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    text = get_super_test_in_str(super_test)

    if len(super_test.tests_id) > 0:
        keyb = get_create_stest_keyb()
    else:
        keyb = get_access_descr_stest_keyb()

    await save_data_end_edit_msg(state, None, bot, data, msg.chat.id, text, keyb)


@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция отменяет любое действие пользователя и ПОЛНОСТЬЮ очищает стейт"""
    data = await state.get_data()
    await bot.delete_message(calb.message.chat.id, data['create_test_msg_id'])
    await state.clear()
    await calb.message.answer("Вы отменили действие")


@router.callback_query(F.data == "add_test")
async def access_super_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция получает все тесты пользователя, удаляет из них те, что есть в создаваемом супер-тесте, если есть не
       добавленные тесты, то предлагает выбор добавления готовых тестов, либо создание нового"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    user_tests = DAO.Test.get_for_user_tid(calb.message.from_user.id)
    #  Тесты, чьи индексы есть в списке супер-теста удаляем из списка
    for i in range(len(user_tests) - 1, -1, -1):  # Идём с конца, чтобы индексы не сбивались
        if user_tests[i].id in super_test.tests_id:
            del user_tests[i]
    #  Если у пользователя есть созданные и не использованные в создаваемом супер-тесте тесты, тогда предлагаем ему их
    #  использовать, иначе выводим сообщение для создания нового теста
    if len(user_tests) != 0:
        await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id,
                                     "Хотите использовать готовые вопросы?",
                                     get_test_selection())
    else:
        await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id,
                                     "Выберите тип теста:\n1\\) С готовыми ответами\n2\\) Без них",
                                     get_test_types_keyb())


@router.callback_query(F.data == "create_new_test")
async def create_new_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Выводит сообщение с выбором типа теста, для создания нового теста"""
    data = await state.get_data()
    await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id,
                                 "Выберите тип вопроса:\n1\\) С готовыми ответами\n2\\) Без них",
                                 get_test_types_keyb())

@router.callback_query(F.data == "add_created_test_menu")
async def add_created_test_menu(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция вывода меню с пагинацией, для добавления уже имеющихся у пользователя тестов в супер-тест"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    user_tests = DAO.Test.get_for_user_tid(calb.message.from_user.id)
    names = []
    indexes = []
    #  Тесты, чьи индексы есть в списке супер-теста удаляем из списка и парсим данные по спискам названий и индексов
    for i in range(len(user_tests) - 1, -1, -1):  # Идём с конца, чтобы индексы не сбивались
        if user_tests[i].id in super_test.tests_id:
            del user_tests[i]
        else:
            names.append(user_tests[i].name)
            indexes.append(user_tests[i].id)
    #  Проверка на случай, если длина списка тестов меньше единицы
    if len(user_tests) < 1:
        await calb.answer("Найден баг, сообщите в ТП, что вы делали чтобы его получить")
        return

    pagin = await create_pagination(state, names, indexes, "add_created_test_", "add_test")
    data = await state.get_data()
    await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id, pagin[0], pagin[1])

@router.callback_query(F.data.startswith("add_created_test_"))
async def add_created_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция заносит уже готовый тест из БД в создаваемый супер-тест"""
    test_id = int(calb.data.split('_')[3])
    test = DAO.Test.get(test_id)
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    super_test.tests_id.append(test_id)
    text = Text(f"Вопрос ", Code(test.name), " добавлен").as_markdown()

    await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id, text,
                                 get_del_or_accept_test_keyb(test_id))

@router.callback_query(F.data.startswith("delete_test_"))
async def delete_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция удаляет тест из создаваемого супер-теста"""
    data = await state.get_data()
    test_id = int(calb.data.split("_")[2])
    super_test: SuperTest = data['new_super_test']
    if test_id not in super_test.tests_id:
        await calb.answer("Вопроса уже нету в тесте")
    else:
        super_test.tests_id.remove(test_id)
        if len(super_test.tests_id) == 0:
            keyb = get_access_descr_stest_keyb()
        else:
            keyb = get_create_stest_keyb()

        text = get_super_test_in_str(super_test)
        await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id, text, keyb)

@router.callback_query(F.data.startswith("test_type_"))
async def set_test_type(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция по каллбеку создаёт тест, устанавливает ему """
    data = await state.get_data()
    str_type = calb.data.split("_")[2]
    test_type = get_str_test_type(str_type)
    if test_type is None:
        await calb.answer("Тип вопроса не найден")
    else:
        data['new_test'] = Test(None, test_type, None, None, calb.from_user.id, None, None)
        text = Text("Введите название вопроса, которое будет отображаться в меню, его будете видеть только вы.").as_markdown()
        await save_data_end_edit_msg(state, Get.TestName, bot, data, calb.message.chat.id, text, get_skip_test_name_keyb())


@router.callback_query(F.data == "skip_test_name")
async def none_test_name(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция пропускает ввод названия теста и просит ввести название теста"""
    data = await state.get_data()
    test: Test = data["new_test"]
    test.name = ""
    await save_data_end_edit_msg(state, Get.TestDescr, bot, data, calb.message.chat.id, "Введите текст вопроса")


@router.message(Get.TestName)
async def get_test_name(msg: Message, state: FSMContext, bot: Bot):
    """Функция принимает название теста и просит ввести название теста"""
    data = await state.get_data()
    test: Test = data["new_test"]
    test.name = msg.text
    await save_data_end_edit_msg(state, Get.TestDescr, bot, data, msg.chat.id, "Введите текст вопроса")
    await msg.delete()


@router.message(Get.TestDescr)
async def get_test_text(msg: Message, state: FSMContext, bot: Bot):
    """Функция получает текст теста, и если название теста пустое, то присваивает ему значение первых 15 символов текста"""
    data = await state.get_data()
    test: Test = data["new_test"]
    test.text = msg.text

    # Если название теста пустое, то присваиваем ему значение в виде первый 15 символов его текста
    if test.name == "":
        if len(test.text) <= 16:  # Если длина текста менее 16 символов, тогда присваиваем названию теста значение описания
            test.name = test.text
        else:
            test.name = test.text[0:15] + "..."

    if test.type == TestType.Quiz:
        await save_data_end_edit_msg(state, Get.TestAnswers, bot, data, msg.chat.id,
                                "Введите через точку с запятой ответы, первыми расположив верные варианты ответа")
    elif test.type == TestType.FreeAnswerQuiz:
        await save_data_end_edit_msg(state, Get.TestAnswers, bot, data, msg.chat.id,
                                "Введите один корректный вариант ответа, либо несколько через точку с запятой")
    await msg.delete()


@router.message(Get.TestAnswers)
async def get_answers(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    test: Test = data["new_test"]
    variants = msg.text.split(";")
    # Проверка на случай, если кол-во ответов меньше 2
    if test.type == TestType.FreeAnswerQuiz and len(variants) < 1:
        await poosh_msg(msg, "Количество ответов не может быть меньше одного")
        return
    elif len(variants) < 2 and test.type == TestType.Quiz:
        await poosh_msg(msg, "Количество ответов не может быть меньше двух")
        return
    # Удаляем лишние пробелы по краям
    test.variants = [var.strip() for var in variants]
    # Удаляем пустые строки из списка
    space_count = test.variants.count("")
    for i in range(space_count):
        test.variants.remove("")

    if test.type == TestType.Quiz:
        await save_data_end_edit_msg(state, Get.TestCountCorrect, bot, data, msg.chat.id,
                                 "Введите число верных ответов")
    elif test.type == TestType.FreeAnswerQuiz:
        text = get_test_in_str(test)
        test.count_of_correct = len(test.variants)
        await save_data_end_edit_msg(state, None, bot, data, msg.chat.id, text, get_final_test_keyb_v2())

    await msg.delete()


@router.message(Get.TestCountCorrect)
async def get_count_of_correct(msg: Message, state: FSMContext, bot: Bot):
    """Функция получает кол-во правильных ответов на тест и заносит это число в память"""
    data = await state.get_data()
    test: Test = data["new_test"]

    try:
        count = int(msg.text)
    except ValueError:
        await poosh_msg(msg, "Вы ввели некорректное число")
        return

    if count < 1:
        await poosh_msg(msg, "Число правильных ответов не может быть меньше одного")
    elif count > len(test.variants):
        await poosh_msg(msg, "Количество правильных ответов не может быть больше общего количества ответов")
    else:
        test.count_of_correct = count
        text = get_test_in_str(test)
        await save_data_end_edit_msg(state, None, bot, data, msg.chat.id, text, get_final_test_keyb())
        await msg.delete()

@router.callback_query(F.data.startswith("test_edit_"))
async def test_redirect_edit(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция направляет на редактирование того или иного параметра теста"""
    data = await state.get_data()
    parameter = calb.data.split("_", 2)[2]
    test: Test = data['new_test']

    match parameter:
        case "name":
            new_state, text = Get.TestEditName, "Введите название вопроса, его будете видеть только вы"
        case "text":
            new_state, text = Get.TestEditDescr, "Введите текст вопроса"
        case "answers":
            if test.type == TestType.Quiz:
                new_state, text = Get.TestEditAnswers, "Введите ответы через точку с запятой, первыми расположив верные варианты ответа"
            else:
                new_state, text = Get.TestEditAnswers, "Введите ответы через точку с запятой"
        case "count_of_correct":
            new_state, text = Get.TestCountCorrect, "Введите число верных ответов"
        case _:
            await calb.answer("Странный у тебя каллбек!")
            return

    await save_data_end_edit_msg(state, new_state, bot, data, calb.message.chat.id, text, get_cancel_edit_test())


@router.message(StateFilter(Get.TestEditName, Get.TestEditDescr, Get.TestEditAnswers))
async def test_edit(msg: Message, state: FSMContext, bot: Bot):
    """Функция изменяет тот или иной параметр теста на указанное значение"""
    data = await state.get_data()
    test: Test = data['new_test']
    match await state.get_state():
        case Get.TestEditName:
            test.name = msg.text
        case Get.TestEditDescr:
            test.text = msg.text
        case Get.TestEditAnswers:
            variants = msg.text.split(";")
            if len(variants) <= 1 and test.type == TestType.Quiz:
                await poosh_msg(msg, "Количество вариантов ответов не может быть меньше двух")
                return
            else:
                test.variants = [var.strip() for var in variants]
    text = get_test_in_str(test)

    if test.type == TestType.Quiz:
        keyb = get_final_test_keyb()
    else:
        keyb = get_final_test_keyb_v2()

    await msg.delete()
    await save_data_end_edit_msg(state, None, bot, data, msg.chat.id, text, keyb)


@router.callback_query(lambda calb: calb.data in ['test_delete', 'test_accept'])
async def test_delete_or_accept(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция удаляет или добавляет в супер-тест создаваемый тест, и перенаправляет на создание нового теста или выбор: создание или окончания создания тестов"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    test: Test = data['new_test']

    if calb.data == "test_delete":
        del data['new_test']
        text = "Вопрос удалён"
    elif calb.data == "test_accept":
        test_id = DAO.Test.add(test)
        super_test.tests_id.append(test_id)
        text = "Вопрос создан"
    else:
        await calb.answer("Странный у вас каллбек!")
        return

    if len(super_test.tests_id) < 1:
        await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id,
                                     text + "\nВыберите тип вопроса:\n1\\) С готовыми ответами\n2\\) Без них",
                                     get_test_types_keyb())
    else:
        await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id,
                                     text + "\nСоздать ещё вопрос?", get_question_create_test())


@router.callback_query(F.data == "create_new_test_decline")
async def decline_creating_new_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция отмены создания нового теста, возвращает меню редактирования супер-теста"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    text = get_super_test_in_str(super_test)
    await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id, text, get_create_stest_keyb())


@router.callback_query(F.data == "cancel_test_edit")
async def cancel_edit_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция отменяет редактирование теста и возвращает меню его подтверждения"""
    data = await state.get_data()
    test: Test = data['new_test']
    text = get_test_in_str(test)
    await save_data_end_edit_msg(state, None, bot, data, calb.message.chat.id, text, get_final_test_keyb())


@router.callback_query(F.data == "access_create_super_test")
async def access_create_super_test(calb: CallbackQuery, state: FSMContext, bot: Bot):
    """Функция добавляет тест в БД, создаёт ссылку на супер-тест с QR-кодом и возвращает их в двух сообщениях пользователю"""
    data = await state.get_data()
    super_test: SuperTest = data['new_super_test']
    super_test_id = DAO.SuperTest.add(super_test)
    super_test_hex = convert_stest_id(super_test_id)  # "красивое" представление id теста * на 45348 в 16-ричной СЧ
    # Создаём ссылку на тест и QR-код
    test_link = f"https://t.me/TestsProjectBot?start={super_test_hex}"
    test_link_qr = generate_custom_qr_code(test_link)
    photo = BufferedInputFile(test_link_qr.getvalue(), f"Test-{super_test_hex}.png")
    test_link_qr.close()
    # Возвращаем результат
    await calb.message.delete()
    await bot.send_photo(calb.message.chat.id, photo, caption=f"Тест создан!\nСсылка: {test_link}")
    # await calb.message.answer(test_link)
