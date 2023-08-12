from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from models import ProblemWords
from variables import *
from config import buttons as btns, messages as ms, MIN_GOAL, MAX_GOAL
from keyboards import yes_no_kb, main_kb, stress_goal_kb, settings_kb, get_stress_kb
from db import db
import random
from handlers.FSM import FSM_stress, FSM_settings, FSM_words
from utils import send_stress
from aiogram.utils.deep_linking import get_start_link



async def get_stress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        right_word = data['right_word']
        if message.text == btns['back']:
            await message.reply(ms['menu'], reply=False, reply_markup=main_kb)
            await state.finish()
            return
        if message.text == right_word.value or message.text.lower() == right_word.value.lower():
            user_id = db.users.get_by_tg(message.from_user.id)
            right = message.text == right_word.value
            word = None
            first_problem = False
            if db.stress.check_problem_cnt(user_id):
                problem_ids = db.stress.get_problem_word_ids(user_id)
                first_problem = True
                print('p_ids', problem_ids)
                if len(problem_ids) != 0:
                    problem_stress.append(ProblemWords(user_id, set(problem_ids)))
                print(problem_stress)
            if check_in_pstress(user_id):
                if not first_problem:
                    if right:
                        db.stress.remove_problem_word(user_id, right_word.id)
                    problem_stress[get_pstress_i(user_id)].words.remove(right_word.id)
                print('p_words', problem_stress)
                if check_pstress_empty(user_id):
                    problem_stress.remove(ProblemWords(user_id, set()))
                    rand = random.randint(1, db.stress.get_words_len())
                    word = db.stress.get_word(rand)
                    db.stress.problem_counter(user_id)
                    print('p_words', problem_stress)
                else:
                    word = db.stress.get_word(list(get_pstress(user_id).words)[0])
            else:
                rand = random.randint(1, db.stress.get_words_len())
                word = db.stress.get_word(rand)
                db.stress.problem_counter(user_id)
            await send_stress(message, word, True, right_word)
            if not check_in_pstress(user_id) and not right:
                db.stress.add_to_problem_words(user_id, right_word.id)
            db.stress.log_word_guess(db.users.get_by_tg(message.from_user.id), right_word.id, message.text, right)
            if db.stress.check_goal(db.users.get_by_tg(message.from_user.id)):
                await message.reply(ms['goal_reach'], reply=False)
            async with state.proxy() as data:
                data['right_word'] = word
            await FSM_stress.word.set()
        else:
            await message.reply(ms['retry'], reply=False)
            await FSM_stress.word.set()

async def settings(message: types.Message, state: FSMContext):
    if message.text == btns['reset_stats']:
        await message.reply(ms['sure'], reply=False, reply_markup=yes_no_kb)
        await FSM_settings.sure.set()
    elif message.text == btns['words_goal']:
        current_goal = db.stress.get_words_goal(db.users.get_by_tg(message.from_user.id))
        await message.reply(ms['set_goal_input'].format(current_goal), reply=False, reply_markup=stress_goal_kb, parse_mode="MarkdownV2")
        await FSM_settings.goal_set.set()
    elif message.text == btns['get_ref_link']:
        ref_link = await get_start_link(str(db.users.get_by_tg(message.from_user.id)), encode=True)
        await message.answer(ref_link)
    else:
        await message.reply(ms['main_menu'], reply=False, reply_markup=main_kb)
        await state.finish()

async def yes_no_reset(message: types.Message, state: FSMContext):
    if message.text == btns['yes']:
        db.stress.reset_stats(db.users.get_by_tg(message.from_user.id))
        await message.reply(ms['stats_reset'], reply=False, reply_markup=settings_kb)
    else:
        await message.reply(ms['cancel'], reply=False, reply_markup=settings_kb)
    await FSM_settings.settings.set()

async def stress_goal(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.reply(ms['settings'], reply=False, reply_markup=settings_kb)
        await FSM_settings.settings.set()
        return
    if not message.text.isdigit():
        await message.reply(ms['retry'], reply=False)
        await FSM_settings.goal_set.set()
        return
    if MIN_GOAL > int(message.text) or int(message.text) > MAX_GOAL:
        await message.reply(ms['wrong_new_goal'], reply=False)
        await FSM_settings.goal_set.set()
        return
    db.stress.set_words_goal(db.users.get_by_tg(message.from_user.id), message.text)
    await message.reply(ms['new_goal'], reply=False, reply_markup=settings_kb)
    await FSM_settings.settings.set()



async def get_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        last_word = data['word']
        if message.text == btns['back']:
            await message.answer(ms['menu'], reply_markup=main_kb)
            await state.finish()
            return
        rand = random.randint(1, db.words.get_words_len())
        word = db.words.get_word(rand)
        user_id = db.users.get_by_tg(message.from_user.id)
        db.users.sub_ad_count(user_id)
        #right = message.text.lower().replace('ё', 'е') == last_word.correct.lower().replace('ё', 'е')
        await send_stress(message, word, False, right_word=last_word)
        async with state.proxy() as data:
            data['word'] = word


def reg_fsm(dp: Dispatcher):
    dp.register_message_handler(get_stress, state=FSM_stress.word)
    dp.register_message_handler(settings, state=FSM_settings.settings)
    dp.register_message_handler(yes_no_reset, state=FSM_settings.sure)
    dp.register_message_handler(stress_goal, state=FSM_settings.goal_set)
    dp.register_message_handler(get_word, state=FSM_words.word)
