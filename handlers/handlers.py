from aiogram import Dispatcher, types
from aiogram.types import ParseMode

from keyboards import main_kb, get_profile_inline,settings_kb, stress_goal_kb, show_profile
from config import commands, MAX_PROBLEM_WORDS, messages as ms, SHOW_SUBSCR_AD, MONEY_FOR_REFERAL
import random
from db import db
from aiogram.dispatcher import FSMContext
from handlers.FSM import FSM_settings, FSM_stress, FSM_words
from variables import problem_stress, check_in_pstress, check_pstress_empty, get_pstress
from models import ProblemWords
from utils import send_stress
from aiogram.utils.deep_linking import decode_payload

async def start(message: types.Message):
    ref_msg = ''
    if not db.users.check_user_exists(message.from_user.id):
        db.users.reg_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
        db.users.set_sub_ad(db.users.get_by_tg(message.from_user.id), SHOW_SUBSCR_AD)
        args = message.get_args()
        if args != '':
            referal = decode_payload(args)
            print(referal)
            db.users.set_referal(message.from_user.id, referal)
            ref_msg = f"Ваc пригласил @{db.users.get_username_by_tg_id(referal)}"
            db.add_money(db.users.get_by_tg(referal), MONEY_FOR_REFERAL)
    await message.reply(ms['welcome'].format(message.from_user.first_name, db.stress.get_words_goal(db.users.get_by_tg(message.from_user.id)), ref_msg), reply_markup=main_kb, reply=False)

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
            problem_stress.append(ProblemWords(user_id, set(problem_ids)))
        print(problem_ids)
    if check_in_pstress(user_id):
        print('p_words', problem_stress)
        if check_pstress_empty(user_id):
            problem_stress.remove(ProblemWords(user_id, set()))
            rand = random.randint(1, db.stress.get_words_len())
            word = db.stress.get_word(rand)
            db.stress.problem_counter(user_id)
        else:
            word = db.stress.get_word(list(get_pstress(user_id).words)[0])
    else:
        if check_pstress_empty(user_id):
            problem_stress.remove(ProblemWords(user_id, set()))
        rand = random.randint(1, db.stress.get_words_len())
        word = db.stress.get_word(rand)
    await send_stress(message, word, True)
    async with state.proxy() as data:
        data['right_word'] = word
    await FSM_stress.word.set()


async def words_cmd(message: types.Message, state: FSMContext):
    rand = random.randint(1, db.words.get_words_len())
    word = db.words.get_word(rand)
    await send_stress(message, word, False)
    async with state.proxy() as data:
        data['word'] = word
    await FSM_words.word.set()


async def profile_cmd(message: types.Message, state: FSMContext):
    await show_profile(message, False, message.from_user.id)


async def settings_cmd(message: types.Message, state: FSMContext):
    await message.reply(ms['settings'], reply_markup=settings_kb, reply=False)
    await FSM_settings.settings.set()


commands_func = [stress_cmd, words_cmd, profile_cmd, settings_cmd]


def reg_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(all_msgs)

