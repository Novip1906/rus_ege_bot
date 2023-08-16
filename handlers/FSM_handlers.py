import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import config
import utils
from models import ProblemWords
from variables import *
from config import buttons as btns, messages as ms, MIN_GOAL, MAX_GOAL, admin_messages as ams, REPORT_MAX_LEN
from keyboards import yes_no_kb, main_kb, stress_goal_kb, get_settings_inl_kb
from db import db
import random
from handlers.FSM import FSM_stress, FSM_settings, FSM_words, FSM_stress_goal, FSM_add_word, FSM_words_goal, FSM_report, FSM_sub_channel
from utils import send_word
from aiogram.utils.deep_linking import get_start_link, decode_payload


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
            if db.stress.check_problem_cnt(message.from_user.id):
                problem_ids = db.stress.get_problem_word_ids(user_id)
                first_problem = True
                if len(problem_ids) != 0:
                    problem_stress.append(ProblemWords(user_id, set(problem_ids)))
            if check_in_pstress(user_id):
                if not first_problem:
                    if right:
                        db.stress.remove_problem_word(user_id, right_word.id)
                    problem_stress[get_pstress_i(user_id)].words.remove(right_word.id)
                if check_pstress_empty():
                    problem_stress.remove(ProblemWords(user_id, set()))
                    rand = random.randint(1, db.stress.get_words_len())
                    word = db.stress.get_word(rand)
                    db.stress.problem_counter(user_id)
                else:
                    word = db.stress.get_word(list(get_pstress(user_id).words)[0])
            else:
                rand = random.randint(1, db.stress.get_words_len())
                word = db.stress.get_word(rand)
                db.stress.problem_counter(user_id)
            await send_word(message, word, True, right_word)
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

# async def settings(message: types.Message, state: FSMContext):
#     if message.text == btns['reset_stats']:
#         await message.reply(ms['sure'], reply=False, reply_markup=yes_no_kb)
#         await FSM_settings.sure.set()
#     elif message.text == btns['stress_goal']:
#         current_goal = db.stress.get_words_goal(db.users.get_by_tg(message.from_user.id))
#         await message.reply(ms['set_goal_input'].format(current_goal), reply=False, reply_markup=stress_goal_kb, parse_mode="MarkdownV2")
#         await FSM_settings.goal_set.set()
#     elif message.text == btns['get_ref_link']:
#         ref_link = await get_start_link(str(db.users.get_by_tg(message.from_user.id)), encode=True)
#         await message.answer(ref_link)
#     else:
#         await message.reply(ms['main_menu'], reply=False, reply_markup=main_kb)
#         await state.finish()

async def yes_no_reset(message: types.Message, state: FSMContext):
    if message.text == btns['yes']:
        db.stress.reset_stats(db.users.get_by_tg(message.from_user.id))
        await message.reply(ms['stats_reset'], reply=False)
    else:
        await message.reply(ms['cancel'], reply=False)
    await FSM_settings.settings.set()

async def stress_goal(message: types.Message, state: FSMContext):
    sub_status = db.users.check_sub(message.from_user.id)
    if message.text == btns['back']:
        await message.answer(ms['cancel'], reply_markup=main_kb)
        await message.answer(ms['settings'], reply_markup=get_settings_inl_kb(sub_status))
        await state.finish()
        return
    if not message.text.isdigit():
        await message.answer(ms['retry'])
        await FSM_stress_goal.goal.set()
        return
    if MIN_GOAL > int(message.text) or int(message.text) > MAX_GOAL:
        await message.answer(ms['wrong_new_goal'])
        await FSM_stress_goal.goal.set()
        return
    db.stress.set_words_goal(message.from_user.id, message.text)
    await message.answer(ms['new_goal'], reply_markup=main_kb)
    await message.answer(ms['settings'], reply_markup=get_settings_inl_kb(sub_status))
    await state.finish()

async def words_goal(message: types.Message, state: FSMContext):
    sub_status = db.users.check_sub(message.from_user.id)
    if message.text == btns['back']:
        await message.answer(ms['cancel'], reply_markup=main_kb)
        await message.answer(ms['settings'], reply_markup=get_settings_inl_kb(sub_status))
        await state.finish()
        return
    if not message.text.isdigit():
        await message.answer(ms['retry'])
        await FSM_words_goal.goal.set()
        return
    if MIN_GOAL > int(message.text) or int(message.text) > MAX_GOAL:
        await message.answer(ms['wrong_new_goal'])
        await FSM_words_goal.goal.set()
        return
    db.words.set_words_goal(message.from_user.id, message.text)
    await message.answer(ms['new_goal'], reply_markup=main_kb)
    await message.answer(ms['settings'], reply_markup=get_settings_inl_kb(sub_status))
    await state.finish()


async def get_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        last_word = data['right_word']
        if message.text == btns['back']:
            await message.reply(ms['menu'], reply=False, reply_markup=main_kb)
            await state.finish()
            return
        user_id = db.users.get_by_tg(message.from_user.id)
        right = message.text.lower().replace('ё', 'е') == last_word.correct.lower().replace('ё', 'е')
        word = None
        first_problem = False
        if not right:
            db.users.sub_ad_count(message.from_user.id)
        if db.words.check_problem_cnt(message.from_user.id):
            problem_ids = db.words.get_problem_word_ids(message.from_user.id)
            first_problem = True
            if len(problem_ids) != 0:
                problem_words.append(ProblemWords(user_id, set(problem_ids)))
        if check_in_pwords(user_id):
            if not first_problem:
                if right:
                    db.words.remove_problem_word(message.from_user.id, last_word.id)
                problem_words[get_pwords_i(user_id)].words.remove(last_word.id)
            if check_pwords_empty():
                problem_words.remove(ProblemWords(user_id, set()))
                rand = random.randint(1, db.words.get_words_len())
                word = db.words.get_word(rand)
                db.words.problem_counter(user_id)
            else:
                word = db.words.get_word(list(get_pwords(user_id).words)[0])
        else:
            rand = random.randint(1, db.stress.get_words_len())
            word = db.words.get_word(rand)
            db.words.problem_counter(user_id)
        await send_word(message, word, False, last_word)
        if not check_in_pwords(user_id) and not right:
            db.words.add_to_problem_words(message.from_user.id, last_word.id)
        db.words.log_word_guess(message.from_user.id, last_word.id, message.text, right)
        if db.words.check_goal(message.from_user.id):
            await message.answer(ms['goal_reach'])
        async with state.proxy() as data:
            data['right_word'] = word
        await FSM_words.word.set()

async def add_word(message: types.Message, state: FSMContext):
    word = message.text
    if word == btns['back']:
        await message.answer(ms['main_menu'], reply_markup=main_kb)
        await state.finish()
        return
    if word == '':
        await message.answer(ms['retry'])
        await FSM_add_word.word.set()
        return
    if db.words.check_word_exists(word):
        await message.answer(ms['add_word_exists'])
        await FSM_add_word.word.set()
        return
    id = db.words.add_new_word(message.from_user.id, word)
    await message.answer(ms['add_word_to_approve'])
    await utils.send_message_to_admin(ams['add_word'].format(id, message.from_user.id, word))
    await FSM_add_word.word.set()

async def get_report(message: types.Message, state: FSMContext):
    if message.text == btns['back']:
        await message.answer(ms['cancel'], reply_markup=main_kb)
        await state.finish()
        return
    if len(message.text) > config.REPORT_MAX_LEN:
        await message.answer(ms['report_max_len'])
        await FSM_report.text.set()
        return
    await message.answer(ms['sure'], reply_markup=yes_no_kb)
    async with state.proxy() as data:
        data['text'] = message.text
    await FSM_report.yes_no.set()

async def yes_no_report(message: types.Message, state: FSMContext):
    if message.text == btns['yes']:
        async with state.proxy() as data:
            id = db.report.add_report(message.from_user.id, data['text'])
            await utils.send_message_to_admin(ams['report'].format(id, message.from_user.id, data['text']))
        await message.answer(ms['report_sent'], reply=False, reply_markup=main_kb)
    else:
        await message.answer(ms['cancel'], reply=False, reply_markup=main_kb)
    await state.finish()

async def check_sub_channel(message: types.Message, state: FSMContext):
    if not (await utils.check_sub_channel(message.from_user.id)):
        await message.answer(ms['not_subscribed'])
        await FSM_sub_channel.check.set()
        return
    db.users.reg_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    db.users.set_sub_ad(db.users.get_by_tg(message.from_user.id), config.SHOW_SUBSCR_AD)
    async with state.proxy() as data:
        args = data['args']
        ref_msg = ''
        if args != '':
            referal = decode_payload(args)
            db.users.set_referal(message.from_user.id, referal)
            ref_msg = f"Ваc пригласил @{db.users.get_username_by_tg_id(referal)}"
            db.users.add_money(referal, config.MONEY_FOR_REFERAL)
            await utils.notify_about_ref(referal)
            logging.info(f"[{message.from_user.id}] NEW USER")
        await message.answer(ms['welcome'].format(message.from_user.first_name,
                                                 db.stress.get_words_goal(db.users.get_by_tg(message.from_user.id)),
                                                 ref_msg), reply_markup=main_kb)


def reg_fsm(dp: Dispatcher):
    dp.register_message_handler(get_stress, state=FSM_stress.word)
    #dp.register_message_handler(settings, state=FSM_settings.settings)
    dp.register_message_handler(yes_no_reset, state=FSM_settings.sure)
    dp.register_message_handler(stress_goal, state=FSM_stress_goal.goal)
    dp.register_message_handler(words_goal, state=FSM_words_goal.goal)
    dp.register_message_handler(get_word, state=FSM_words.word)
    dp.register_message_handler(add_word, state=FSM_add_word.word)
    dp.register_message_handler(get_report, state=FSM_report.text)
    dp.register_message_handler(yes_no_report, state=FSM_report.yes_no)
    dp.register_message_handler(check_sub_channel, state=FSM_sub_channel.check)
