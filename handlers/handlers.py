from aiogram import Dispatcher, types
from keyboards import main_kb, get_stress_kb, get_stats_p_choose_inline, words_kb, settings_kb, stress_goal_kb
from config import commands, MAX_PROBLEM_WORDS, messages as ms, SHOW_SUBSCR_AD
import random
from db import db
from aiogram.dispatcher import FSMContext
from handlers.FSM import FSM_settings, FSM_stress, FSM_words
from variables import problem_words, check_in_pwords, check_pwords_empty, get_pword
from models import ProblemWords
from utils import send_stress

async def start(message: types.Message):
    if not db.users.check_user_exists(message.from_user.id):
        db.users.reg_user(message.from_user.id, message.from_user.first_name)
        db.users.set_sub_ad(db.users.get_by_tg(message.from_user.id), SHOW_SUBSCR_AD)
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
    user_id = db.users.get_by_tg(message.from_user.id)
    word = None
    if db.stress.check_problem_cnt(user_id):
        problem_ids = db.stress.get_problem_word_ids(user_id)
        print('p_ids', problem_ids)
        if len(problem_ids) != 0:
            problem_words.append(ProblemWords(user_id, set(problem_ids)))
        print(problem_ids)
    if check_in_pwords(user_id):
        print('p_words', problem_words)
        if check_pwords_empty(user_id):
            problem_words.remove(ProblemWords(user_id, set()))
            rand = random.randint(1, db.stress.get_words_len())
            word = db.stress.get_word(rand)
            db.stress.problem_counter(user_id)
        else:
            word = db.stress.get_word(list(get_pword(user_id).words)[0])
    else:
        if check_pwords_empty(user_id):
            problem_words.remove(ProblemWords(user_id, set()))
        rand = random.randint(1, db.stress.get_words_len())
        word = db.stress.get_word(rand)
    await send_stress(message, word)
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

