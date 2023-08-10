from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from create_bot import bot
from config import buttons as btns, messages as ms, MIN_GOAL, MAX_GOAL
from keyboards import yes_no_kb, main_kb, stress_goal_kb, settings_kb, get_stress_kb
from db import db
import random
from handlers.FSM import FSM_stress, FSM_settings, FSM_words


def check_for_mkv2(text: str) -> str:
    if '_' in text:
        i = text.index('_')
        return text[:i] + "\\" + text[i:]

async def get_stress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        right_word = data['right_word']
        if message.text == btns['back']:
            await message.reply(ms['menu'], reply=False, reply_markup=main_kb)
            await state.finish()
            return
        if message.text == right_word.value or message.text.lower() == right_word.value.lower():
            rand = random.randint(1, db.stress.get_words_len())
            word = db.stress.get_word(rand)
            right = message.text == right_word.value
            comment = ''
            new_comment = ''
            explain = ''
            if right_word.comment_exists():
                comment = f"\({right_word.comment}\)"
            if word.comment_exists():
                new_comment = f"\({word.comment}\)"
            ans = ms['right'].format(word.value.lower(), new_comment, '') if right else (ms['wrong'].format(right_word.value, comment, explain, word.value.lower(), new_comment, ''))
            await message.reply(ans, reply=False, reply_markup=get_stress_kb(word.value.lower()), parse_mode='MarkdownV2')
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
            await message.reply(ms['menu'], reply=False, reply_markup=main_kb)
            await state.finish()
            return
        rand = random.randint(1, db.words.get_words_len())
        word = db.words.get_word(rand)
        user_id = db.users.get_by_tg(message.from_user.id)
        db.users.sub_ad_count(user_id)
        explain = 'Пояснение: 🔒\n'
        sub_ad = ''
        if db.users.check_sub_ad(user_id):
            sub_ad = f'\n{ms["sub_ad"]}'
        comment, new_comment = '', ''
        right = message.text.lower() == last_word.correct.lower()
        answer = ms['right'].format(word.word, comment, sub_ad) if right else ms['wrong'].format(last_word.correct, new_comment, explain, word.word, comment, sub_ad)
        answer = check_for_mkv2(answer)
        await message.reply(answer, reply=False, parse_mode='MarkdownV2')


def reg_fsm(dp: Dispatcher):
    dp.register_message_handler(get_stress, state=FSM_stress.word)
    dp.register_message_handler(settings, state=FSM_settings.settings)
    dp.register_message_handler(yes_no_reset, state=FSM_settings.sure)
    dp.register_message_handler(stress_goal, state=FSM_settings.goal_set)
    dp.register_message_handler(get_word, state=FSM_words.word)
