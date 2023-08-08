from create_bot import bot, dp
from aiogram import executor
from handlers import reg_handlers
from keyboards import reg_inline_callbacks
from admin_handlers import reg_admin_handlers
from db import db

reg_admin_handlers(dp)
reg_handlers(dp)
reg_inline_callbacks(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)