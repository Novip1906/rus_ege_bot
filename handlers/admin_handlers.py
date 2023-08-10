from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import buttons as btns
from db import db
from create_bot import bot
from keyboards import yes_no_kb, main_kb

class FSM_gmsg(StatesGroup):
    msg = State()
    sure = State()

async def global_message_cmd(message: types.Message):
    if message.from_user.id == 710810829:
        await message.reply("Сообщение:", reply=False)
        await FSM_gmsg.msg.set()

async def give_sub_cmd(message: types.Message):
    user_id = db.users.get_by_tg(message.from_user.id)
    db.users.add_sub(user_id, 30)
    end = db.users.get_sub_end(user_id)
    await message.answer(f'+30 дней\nДо {end}')



async def get_msg(message: types.Message, state: FSMContext):
    if message.text == '':
        await state.finish()
        return
    async with state.proxy() as data:
        data['msg'] = message.text if message.text is not None else message.caption
        data['photo'] = message.photo[-1].file_id if len(message.photo) > 0 else ''
        await message.reply('Вы уверены?', reply_markup=yes_no_kb)
        await FSM_gmsg.sure.set()

async def yes_no(message: types.Message, state: FSMContext):
    if message.text == btns['yes']:
        tg_ids = [user[1] for user in db.users.get_all_users()]
        for id in tg_ids:
            async with state.proxy() as data:
                if data['photo'] != '':
                    await bot.send_photo(id, data['photo'], caption=data['msg'])
                else:
                    await bot.send_message(id, data['msg'])
        await message.reply("Готово", reply_markup=main_kb)
    else:
        await message.answer('Отмена', reply_markup=main_kb)
    await state.finish()

def reg_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(global_message_cmd, commands=['gmsg'])
    dp.register_message_handler(give_sub_cmd, commands=['givesub'])
    dp.register_message_handler(get_msg, state=FSM_gmsg.msg, content_types=['photo', 'text'])
    dp.register_message_handler(yes_no, state=FSM_gmsg.sure)