import sqlite3 as sql
from bot_classes import *

class DAO:
    _connection = sql.Connection
    _cursor = sql.Cursor

    def __init__(self):
        self._connection = sql.Connection("DataBase\DB.db")
        self._cursor = self._connection.cursor()
        self.User = UserDB(self)
        self.Test = TestDB(self)
        self.SuperTest = SuperTestDB(self)
        self.Answer = AnswersDB(self)
        self._connection = sql.connect("DataBase/DB.db")

class UserDB:
    def __init__(self, main_dao: DAO):
        self.connection = main_dao._connection

    def get_user(self, user_id: int) -> User:
        """Функция возвращает объект пользователя по его tid"""
        cur = self.connection.execute(  # Выполняем запрос через объект курсора
                    """
                    SELECT chat_id, username, name
                    FROM users
                    WHERE tid = ?
                    """, (user_id,))
        data = cur.fetchone()
        user = User(user_id, data[0], data[1], data[2])
        return user

    def check_user(self, user_id: int) -> bool:
        """Функция проверяет наличие пользователя с tid = user_id"""
        cur = self.connection.execute(  # Выполняем запрос через объект курсора
                    """
                    SELECT tid
                    FROM users
                    WHERE tid = ?
                    """, (user_id,))
        return cur.fetchone() is not None

    def add_user(self, user: User) -> None:
        """Функция добавляет в БД запись об игроке с tid = user_id и другими столбцами соответственно"""
        self.connection.execute(
                    """
                    INSERT INTO users (tid, chat_id, username, name)
                    VALUES (?, ?, ?, ?)
                    """, (user.id, user.chat_id, user.username, user.name))
        self.connection.commit()

    def edit_username(self, user_id, username) -> None:
        """Функция изменяет username пользователя с tid = user_id"""
        self.connection.execute(
                    """
                    UPDATE users
                    SET username = ?
                    WHERE tid == ?
                    """, (username, user_id))
        self.connection.commit()

    def edit_name(self, user_id, name) -> None:
        """Функция изменяет имя пользователя с tid = user_id"""
        self.connection.execute(
                    """
                    UPDATE users
                    SET name = ?
                    WHERE tid == ?
                    """, (name, user_id))
        self.connection.commit()


class TestDB:
    def __init__(self, main_dao: DAO):
        self.connection = main_dao._connection

    def get(self, test_id) -> Test | None:
        """Возвращает объект класса Test со значениями теста под id = test_id"""
        cur = self.connection.execute(
                    """
                    SELECT type, text, creator_tid, answers, name, count_of_correct
                    FROM tests
                    WHERE test_id == ?
                    LIMIT 1
                    """, (test_id,))
        data = cur.fetchone()
        variants = data[3].split(";")
        type = get_str_test_type(data[0])
        test = Test(test_id, type, data[1], variants, data[2], data[3], data[4])
        return test

    def multiple_get(self, tests_id: list[int]) -> list[Test]:
        """Возвращает список объектов класса Test со значениями теста под id = id из передаваемого списка"""
        str_tests = f"test_id == {tests_id[0]}"

        for test_id in tests_id[1:]:
            str_tests += f"AND test_id == {test_id}"

        cur = self.connection.execute(
            """
            SELECT type, text, creator_tid, answers, name, count_of_correct, test_id
            FROM tests
            WHERE """ + str_tests + """
            """)
        datas = cur.fetchall()

        tests = []
        for data in datas:
            variants = data[3].split(";")
            type = get_str_test_type(data[0])
            test = Test(data[5], type, data[1], variants, data[2], data[3], data[4])
            tests.append(test)

        return tests

    def get_for_user_tid(self, tid: int) -> list[Test]:
        """Возвращает список тестов пользователя по его tid"""
        cur = self.connection.execute(
            """
            SELECT test_id, type, text, creator_tid, answers, name, count_of_correct
            FROM tests
            WHERE creator_tid
            """)
        datas = cur.fetchall()
        # "Распаковываем" информацию и заносим в класс Test
        tests = []
        for data in datas:
            variants = data[4].split(";")
            type = get_str_test_type(data[1])
            test = Test(data[0], type, data[2], variants, data[3], data[5], data[6])
            tests.append(test)

        return tests


    def add(self, test: Test) -> int:
        """Функция добавляет тест в БД, и возвращает его id"""
        answers = ";".join(test.variants)  # Переводим в строку возможные ответы
        print(test)

        cur = self.connection.execute(
                     """
                    INSERT INTO tests (creator_tid, type, text, answers, name, count_of_correct)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (test.creator_id, test.type.value, test.text, answers, test.name, test.count_of_correct))
        self.connection.commit()
        return cur.lastrowid

    def delete(self, test_id) -> None:
        """Удаляет тест из БД по его id"""
        self.connection.execute(
                    """
                    DELETE FROM tests
                    WHERE test_id == ?
                    """, (test_id,))
        self.connection.commit()

    def multiple_delete(self, tests: list[tuple[int  ]]) -> None:
        """Удаляет тесты, чьи id есть в списке"""
        self.connection.executemany(
                    """
                    DELETE FROM tests
                    WHERE test_id == ?
                    """, tests)
        self.connection.commit()


class SuperTestDB:
    def __init__(self, main_dao: DAO):
        self.connection = main_dao._connection

    def get_for_id(self, stest_id: int) -> SuperTest:
        """Возвращает супер-тест по его id"""
        cur = self.connection.execute(
                    """
                    SELECT creator_tid, tests_id, end_date, description, name
                    FROM super_tests
                    WHERE stest_id == ?
                    LIMIT 1
                    """, (stest_id,))
        data = cur.fetchone()
        tests = data[1].split(";")
        end_date = datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S")
        print(end_date)
        super_test = SuperTest(stest_id, tests, data[0], end_date, data[3], data[4])
        return super_test

    def get_for_user(self, creator_id: int) -> list[SuperTest]:
        """Возвращает список супер-тестов по id их создателя"""
        cur = self.connection.execute(
                    """
                    SELECT stest_id, tests_id, end_date, description, name
                    FROM super_tests
                    WHERE creator_tid == ?
                    """, (creator_id,))
        data = cur.fetchone()
        tests = data[1].split(";")
        end_date = datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S")
        print(end_date)
        super_test = SuperTest(data[0], tests, creator_id, end_date, data[3], data[4])
        return super_test

    def add(self, stest: SuperTest) -> int:
        """Добавляет супер-тест в БД и возвращает его id"""
        str_tests_id = [str(test_id) for test_id in stest.tests_id]
        tests_str = ";".join(str_tests_id)
        end_date = stest.end_date.strftime("%Y-%m-%d %H:%M:%S")
        print(end_date)
        cur = self.connection.execute(
                    """
                    INSERT INTO super_tests (creator_tid, tests_id, end_date, description, name)
                    VALUES (?, ?, ?, ?, ?)
                    """, (stest.creator_id, tests_str, end_date, stest.description, stest.name))
        self.connection.commit()
        return cur.lastrowid

    def delete(self, stest_id: int) -> None:
        """Удаляет супер-тест по его id"""
        self.connection.execute(
                    """
                    DELETE FROM super_tests
                    WHERE stest_id == ?
                    """, (stest_id,))
        self.connection.commit()

class AnswersDB:
    def __init__(self, main_dao: DAO):
        self.connection = main_dao._connection

    def get_for_id(self, answer_id: int) -> LiteUserSuperTestAnswer:
        """Возвращает ответ на супер-тест по id ответа"""
        cur = self.connection.execute(
                    """
                    SELECT user_tid, stest_id, answers
                    FROM answers
                    WHERE answer_id == ?
                    LIMIT 1
                    """, (answer_id,))
        data = cur.fetchone()
        answers = data[2].split(";")
        return LiteUserSuperTestAnswer(answer_id, data[0], data[1], answers)

    def get_for_stest(self, stest_id: int) -> list[UserSuperTestAnswer]:
        """Возвращает список из ответов на супер-тест с данным id"""
        cur = self.connection.execute(
                    """
                    SELECT answer_id, user_tid, answers
                    FROM answers
                    WHERE stest_id == ?
                    """, (stest_id,))
        all_data = cur.fetchall()
        all_answers = []

        for data in all_data:
            answers = data[2].split(";")
            answer = LiteUserSuperTestAnswer(data[0], data[1], stest_id, answers)
            all_answers.append(answer)

        return all_answers


    def get_for_user(self, user_id: int) -> list[UserSuperTestAnswer]:
        """Возвращает все ответы пользователя по его id"""
        cur = self.connection.execute(
                    """
                    SELECT answer_id, user_tid, answers
                    FROM answers
                    WHERE user_tid == ?
                    """, (user_id,))
        all_data = cur.fetchall()
        all_answers = []

        for data in all_data:
            answers = data[2].split(";")
            answer = LiteUserSuperTestAnswer(data[0], user_id, data[1], answers)
            all_answers.append(answer)

        return all_answers

    def get_count(self, stest_id: int) -> int:
        """Функция возвращает кол-во прохождений супер-теста пользователями"""
        cur = self.connection.execute(
                    """
                    SELECT Count(*)
                    FROM answers
                    WHERE stest_id = ?
                    """, (stest_id,))
        data = cur.fetchone()
        return int(data[0])

    def add(self, answer: UserSuperTestAnswer) -> None:
        """Добавляет ответ на супер-тест в БД"""
        str_answers = ";".join(answer.answers)
        self.connection.execute(
                    """
                    INSERT INTO answers (user_tid, stest_id, answers)
                    VALUES (?, ?, ?)
                    """, (answer.user_id, answer.stets_id, str_answers))
        self.connection.commit()

    def delete(self, answer_id: int) -> None:
        """Удаляет ответ из БД по его id"""
        self.connection.execute(
                    """
                    DELETE FROM answers
                    WHERE answer_id == ?
                    """, (answer_id,))
        self.connection.commit()

DAO = DAO()
