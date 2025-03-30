"""В этом модуле содержаться все классы бота"""
import enum
from dataclasses import dataclass
from datetime import datetime
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from io import BytesIO
from math import ceil

class TestType(enum.Enum):
    Quiz = "Quiz"  #
    FreeAnswerQuiz = "FreeAnswerQuiz"  #

def convert_stest_id(stest_id: int) -> str:
    return hex(stest_id * 45348)

def deconvert_stest_id(stest_hex: str) -> int:
    return int(stest_hex, 16) // 45348

def get_str_test_type(type_name: str) -> TestType:
    """Возвращает тип теста, по строке его имени"""
    match type_name:
        case "Quiz": return TestType.Quiz
        case "FreeAnswerQuiz": return TestType.FreeAnswerQuiz

def get_class_test_type(type: TestType):
    """Возвращает тип теста строкой по классу"""
    match type:
        case TestType.Quiz: return "Quiz"
        case TestType.FreeAnswerQuiz: return "FreeAnswerQuiz"

@dataclass
class User:
    id: int
    chat_id: int
    username: str
    name: str


@dataclass
class Test:
    id: int
    type: TestType
    text: str
    variants: list[str]  # Варианты ответа на тест, первый - правильный
    creator_id: int
    name: str
    count_of_correct: int


@dataclass
class SuperTest:
    id: int
    tests_id: list[int]
    creator_id: int
    end_date: datetime
    description: str
    name: str


@dataclass
class UserTestAnswer:
    test_id: int
    answer: list[int]  # id ответа

    def __init__(self, test_id: int, answer: int):
        self.test_id = test_id
        self.answer = answer


@dataclass
class UserSuperTestAnswer:
    id: int
    user_id: int
    stets_id: int
    answers: list[int]


@dataclass
class LiteUserSuperTestAnswer:  # Переделать
    """"""
    id: int
    user_id: int
    stest_id: int
    answers: list[int]


@dataclass
class SuperTestResults:
    """"""
    all_answers: list[UserSuperTestAnswer]


@dataclass
class Pagination:
    """"""
    texts: list[str]
    indexes: list[int]
    callback: str
    back_callback: str
    page_num: int
    items_on_page: int

    def __init__(self, pagination_data: dict):
        self.texts = pagination_data['texts']
        self.indexes = pagination_data['indexes']
        self.callback = pagination_data['callback']
        self.back_callback = pagination_data['back_callback']
        self.page_num = pagination_data['page_num']
        self.items_on_page = pagination_data['items_on_page']

    def get_pagination_data(self) -> dict:
        return {
                'texts': self.texts,
                'indexes': self.indexes,
                'callback': self.callback,
                'back_callback': self.back_callback,
                'page_num': self.page_num,
                'items_on_page': self.items_on_page
        }

    def get_last_page_num(self) -> int:
        return ceil(len(self.texts) / self.items_on_page)



def hex_to_rgb(hex_color: str) -> tuple:
    """Конвертирует HEX-цвет в кортеж RGB."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def generate_custom_qr_code(
        data: str,
        fill_color: str = "#000000",
        back_color: str = "#FFFFFF") -> BytesIO:
    """
    Генерирует QR-код с закруглёнными краями квадратов и пользовательскими цветами.
    Возвращает изображение в виде BytesIO.
    """
    # Конвертируем HEX-цвета в RGB
    fill_rgb = hex_to_rgb(fill_color)
    back_rgb = hex_to_rgb(back_color)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Создаём QR-код с закруглёнными краями и пользовательскими цветами
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            front_color=fill_rgb,
            back_color=back_rgb
        )
    )

    # Сохраняем изображение в BytesIO
    img_byte_array = BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)

    with open("QRCode.png", "wb") as f:
        f.write(img_byte_array.getvalue())

    return img_byte_array