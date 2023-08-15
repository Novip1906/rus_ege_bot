from create_bot import dp
from aiogram import executor
from handlers.handlers import reg_handlers
from handlers.FSM_handlers import reg_fsm
from keyboards import reg_inline_callbacks
from handlers.admin_handlers import reg_admin_handlers
import logging

logging.basicConfig(level=logging.INFO, filename="logs.log",
                    format="%(asctime)s %(levelname)s %(message)s")

reg_admin_handlers(dp)
reg_handlers(dp)
reg_fsm(dp)
reg_inline_callbacks(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)