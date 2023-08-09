from aiogram import Dispatcher, Bot
import config as cfg
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=(cfg.TG_TOKEN if not cfg.TEST else cfg.TG_TOKEN_TEST))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
