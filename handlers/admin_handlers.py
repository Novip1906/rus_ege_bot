from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import json
import utils
from config import buttons as btns, admin_messages as ams, MONEY_FOR_WORD, messages as ms
from db import db
from create_bot import bot
from keyboards import yes_no_kb, main_kb, admin_get_new_word_kb, back_kb


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

class FSM_report_ans(StatesGroup):
    ans = State()


async def global_message_cmd(message: types.Message):
    if db.admin.get_adm_lvl(message.from_user.id) > 0:
        await message.reply("Сообщение:", reply=False)
        await FSM_gmsg.msg.set()

async def ban_cmd(message: types.Message):
    if db.admin.get_adm_lvl(message.from_user.id) > 0:
        args = message.get_args().split(' ')
        if len(args) < 2:
            await message.reply('/ban tg_id days')
            return
        tg_id, days = args[0], args[1]
        if not days.isdigit():
            await message.reply('дни числом надо')
            return
        days = int(days)
        res = db.users.ban(tg_id, days)
        if res:
            await bot.send_message(tg_id, ms['banned'])
            await message.answer("Забанен")
        else:
            await message.answer("ошибка")

async def unban_cmd(message: types.Message):
    if db.admin.get_adm_lvl(message.from_user.id) > 0:
        tg_id = message.get_args()
        if tg_id == '' or tg_id is None:
            await message.reply('/unban tg_id')
            return
        res = db.users.unban(tg_id)
        if res:
            await bot.send_message(tg_id, ms['unbanned'])
            await message.answer('Разбанен')
        else:
            await message.answer("ошибка")

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
        errors = 0
        for id in tg_ids:
            async with state.proxy() as data:
                try:
                    if data['photo'] != '':
                        await bot.send_photo(id, data['photo'], caption=data['msg'])
                    else:
                        await bot.send_message(id, data['msg'])
                except:
                    errors += 1
        await message.reply(f"Готово, ({errors} ошибок)", reply_markup=main_kb)
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
    await utils.send_message_to_admin(f'{message.from_user.id} начал одобрять слово {id}')
    correct, word, comment, explain = db.words.get_new_word(id)
    await message.answer(f'Слово от пользователя: {word}\nСлово с пробелом:', reply_markup=admin_get_new_word_kb(word, True))
    async with state.proxy() as data:
        data['id'] = id
        data['correct'], data['word'], data['comment'], data['explain'] = correct, word, comment, explain
        print(data)
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
            await utils.send_message_to_admin(f'{message.from_user.id} отклонил слово {id}')
            await message.answer('Отклонено', reply_markup=main_kb)
            await state.finish()
            return
        data['word'] = word
        await message.answer('Правильное слово:', reply_markup=admin_get_new_word_kb(data['correct']))
        await FSM_approve_word.correct.set()

async def get_approved_correct(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.answer('Отмена', reply_markup=main_kb)
        await state.finish()
        return
    async with state.proxy() as data:
        data['correct'] = message.text
        await message.answer('Комментарий: ', reply_markup=admin_get_new_word_kb(data['comment'], skip=True))
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
        await message.answer('Пояснение:', reply_markup=admin_get_new_word_kb(data['explain']))
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
        await utils.send_message_to_admin(f'{message.from_user.id} одобрил слово {id}')
        await message.answer('Одобрено!', reply_markup=main_kb)
        await state.finish()

async def report_cmd(message: types.Message, state: FSMContext):
    if db.admin.get_adm_lvl(message.from_user.id) == 0:
        return
    args = message.get_args()
    if args == '':
        await message.answer('Вы забыли id в аргументах к команде')
        return
    id = args
    if not id.isdigit():
        await message.answer('Цифру надо.........')
        return
    r = db.report.get_report(id)
    if r is None:
        await message.reply('такого репорта нет')
        return
    await utils.send_message_to_admin(f'{message.from_user.id} начал отвечать на репорт {id}')
    tg_id, text = r[0], r[1]
    await message.answer(f'text: {text}\n\nВведите сообщение:', reply_markup=back_kb)
    async with state.proxy() as data:
        data['id'] = id
        data['tg_id'] = tg_id
    await FSM_report_ans.ans.set()

async def get_report_ans(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.reply(ms['cancel'], reply_markup=main_kb)
        await state.finish()
        return
    async with state.proxy() as data:
        db.report.answer_report(data['id'], message.from_user.id, message.text)
        await utils.report_answer(data['tg_id'], message.text)
        await utils.send_message_to_admin(f'{message.from_user.id} ответил на репорт {data["id"]}')
        await message.answer('Отправлен!', reply_markup=main_kb)
    await state.finish()



def reg_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(global_message_cmd, commands=['gmsg'])
    dp.register_message_handler(approve_word_cmd, commands=['aw'])
    dp.register_message_handler(report_cmd, commands=['ar'])
    dp.register_message_handler(sql_cmd, commands=['sql'])
    dp.register_message_handler(ban_cmd, commands=['ban'])
    dp.register_message_handler(unban_cmd, commands=['unban'])
    #dp.register_message_handler(give_sub_cmd, commands=['givesub'])
    dp.register_message_handler(get_msg, state=FSM_gmsg.msg, content_types=['photo', 'text'])
    dp.register_message_handler(yes_no, state=FSM_gmsg.sure)
    dp.register_message_handler(get_approved_word, state=FSM_approve_word.word)
    dp.register_message_handler(get_approved_correct, state=FSM_approve_word.correct)
    dp.register_message_handler(get_approved_comment, state=FSM_approve_word.comment)
    dp.register_message_handler(get_approved_explain, state=FSM_approve_word.explain)
    dp.register_message_handler(get_sql, state=FSM_sql.sql)
    dp.register_message_handler(get_report_ans, state=FSM_report_ans.ans)