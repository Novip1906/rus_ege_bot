from aiogram import Dispatcher, types
from keyboards import main_kb, get_stress_kb, get_stats_p_choose_inline, words_kb, settings_kb, stress_goal_kb
from config import commands, MAX_PROBLEM_WORDS, buttons as btns, messages as ms, MIN_GOAL, MAX_GOAL
import random
from db import db
from aiogram.dispatcher import FSMContext
from handlers.FSM import FSM_settings, FSM_stress, FSM_words


async def start(message: types.Message):
    if not db.users.check_user_exists(message.from_user.id):
        db.users.reg_user(message.from_user.id, message.from_user.first_name)
    await message.reply(ms['welcome'].format(message.from_user.first_name, db.stress.get_words_goal(db.users.get_by_tg(message.from_user.id))), reply_markup=main_kb, reply=False)

async def all_msgs(message: types.Message, state: FSMContext):
    text = message.text
    found = False
    for i in range(len(commands)):
        if text in commands[i]:
            await commands_func[i](message, state)
            found = True
    if not found:
        await message.reply(ms['cmd_not_found'])

async def stress_cmd(message: types.Message, state: FSMContext):
    rand = random.randint(1, db.stress.get_words_len())
    word = db.stress.get_word(rand)
    comment = ''
    if word.comment_exists():
        comment = f"({word.comment})"
    ans = ms['first_word'].format('{}', comment)
    await message.answer(ans.format(word.value.lower()), reply_markup=get_stress_kb(word.value.lower()))
    async with state.proxy() as data:
        data['right_word'] = word
    await FSM_stress.word.set()


async def words_cmd(message: types.Message, state: FSMContext):
    rand = random.randint(1, db.words.get_words_len())
    word = db.words.get_word(rand)
    await message.reply(ms['first_word'].format(word.word, ''), reply=False, reply_markup=words_kb)
    async with state.proxy() as data:
        data['word'] = word
    await FSM_words.word.set()


async def stats_cmd(message: types.Message, state: FSMContext):
    user_id = db.users.get_by_tg(message.from_user.id)
    p = [
        db.stress.get_words_count(user_id, 2),
        round(db.stress.get_correct_perc(user_id, 2), 3),
        '\n'.join([f"\t- {word[0]} ({word[1]})" for word in db.stress.get_problem_words(user_id, MAX_PROBLEM_WORDS, 2)])
    ]
    answer = f"Слов: {p[0]}\nПравильность: {p[1]}%\nПроблемные слова:\n{p[2]}"
    await message.reply(answer, reply=False, reply_markup=get_stats_p_choose_inline(2))

async def settings_cmd(message: types.Message, state: FSMContext):
    await message.reply(ms['settings'], reply_markup=settings_kb, reply=False)
    await FSM_settings.settings.set()


commands_func = [stress_cmd, words_cmd, stats_cmd, settings_cmd]


def reg_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(all_msgs)

