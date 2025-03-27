import asyncio
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from DataBase.DAO import DAO
from bot_classes import *

class Get(StatesGroup):
    TestName = State()
