from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import json
import utils
from config import buttons as btns, admin_messages as ams, MONEY_FOR_WORD
from db import db
from create_bot import bot
from keyboards import yes_no_kb, main_kb, admin_get_new_word_kb_word, admin_get_new_word_kb_correct, back_kb, admin_get_new_word_kb_comment

class FSM_gmsg(StatesGroup):
    msg = State()
    sure = State()

class FSM_approve_word(StatesGroup):
    word = State()
    correct = State()
    comment = State()
    explain = State()

class FSM_sql(StatesGroup):
    sql = State()


async def global_message_cmd(message: types.Message):
    if db.admin.get_adm_lvl(message.from_user.id) > 0:
        await message.reply("Сообщение:", reply=False)
        await FSM_gmsg.msg.set()

# async def give_sub_cmd(message: types.Message):
#     db.users.add_sub(message.from_user.id, 30)
#     end = db.users.get_sub_end(message.from_user.id)
#     await message.answer(f'+30 дней\nДо {end}')

async def sql_cmd(message: types.Message):
    if db.admin.get_adm_lvl(message.from_user.id) > 1:
        await message.answer('Введите запрос')
        await FSM_sql.sql.set()

async def get_sql(message: types.Message, state: FSMContext):
    try:
        db.cur.execute(message.text)
        res = db.cur.fetchall()
        db.conn.commit()
        await message.answer(json.dumps(res, indent=2))
    except Exception as e:
        await message.answer('error')
    await state.finish()

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

async def approve_word_cmd(message: types.Message, state: FSMContext):
    args = message.get_args()
    if db.admin.get_adm_lvl(message.from_user.id) == 0:
        return
    if args == '':
        await message.answer('Вы забыли id в аргументах к команде')
        return
    id = args
    if not id.isdigit():
        await message.answer('Цифру надо.........')
        return
    word = db.words.get_new_word(id)
    await message.answer(f'Слово от пользователя: {word}\nСлово с пробелом:', reply_markup=admin_get_new_word_kb_word())
    async with state.proxy() as data:
        data['id'] = id
    await FSM_approve_word.word.set()

async def get_approved_word(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.answer('Отмена', reply_markup=main_kb)
        await state.finish()
        return
    async with state.proxy() as data:
        id = data['id']
        word = message.text
        if word == btns['reject']:
            db.words.set_new_word_approved(id, 2)
            await message.answer('Отклонено', reply_markup=main_kb)
            await state.finish()
            return
        data['word'] = word
        await message.answer('Правильное слово:', reply_markup=admin_get_new_word_kb_correct(db.words.get_new_word(data['id'])))
        await FSM_approve_word.correct.set()

async def get_approved_correct(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.answer('Отмена', reply_markup=main_kb)
        await state.finish()
        return
    async with state.proxy() as data:
        data['correct'] = message.text
        await message.answer('Комментарий: ', reply_markup=admin_get_new_word_kb_comment())
        await FSM_approve_word.comment.set()
async def get_approved_comment(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.answer('Отмена', reply_markup=main_kb)
        await state.finish()
        return
    async with state.proxy() as data:
        comment = message.text
        if comment == btns['skip']:
            comment = ''
        data['comment'] = comment
        await message.answer('Пояснение:', reply_markup=back_kb)
        await FSM_approve_word.explain.set()

async def get_approved_explain(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.answer('Отмена', reply_markup=main_kb)
        await state.finish()
        return
    async with state.proxy() as data:
        id, word, correct, comment = data['id'], data['word'], data['correct'], data['comment']
        db.words.set_new_word_approved(id, 1)
        db.words.write_word(word, correct, comment, message.text)
        tg_id = db.words.get_new_word_tg_id(id)
        db.users.add_money(tg_id, MONEY_FOR_WORD)

        await utils.notify_about_approve(tg_id, correct)
        await message.answer('Одобрено!', reply_markup=main_kb)



def reg_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(global_message_cmd, commands=['gmsg'])
    dp.register_message_handler(approve_word_cmd, commands=['aw'])
    dp.register_message_handler(sql_cmd, commands=['sql'])
    #dp.register_message_handler(give_sub_cmd, commands=['givesub'])
    dp.register_message_handler(get_msg, state=FSM_gmsg.msg, content_types=['photo', 'text'])
    dp.register_message_handler(yes_no, state=FSM_gmsg.sure)
    dp.register_message_handler(get_approved_word, state=FSM_approve_word.word)
    dp.register_message_handler(get_approved_correct, state=FSM_approve_word.correct)
    dp.register_message_handler(get_approved_comment, state=FSM_approve_word.comment)
    dp.register_message_handler(get_approved_explain, state=FSM_approve_word.explain)
    dp.register_message_handler(get_sql, state=FSM_sql.sql)