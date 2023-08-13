from create_bot import dp, bot
from aiogram import types, executor
from db import db

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    admin_lvl = db.get_adm_lvl(message.from_user.id)
    if admin_lvl > 0:
        await message.answer(f'Успешный вход. Уровень: {admin_lvl}')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)