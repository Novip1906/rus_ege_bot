from aiogram import Dispatcher, Bot
import config as cfg
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=cfg.TG_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
