from aiogram import Dispatcher, types
from keyboards import main_kb, get_word_kb, get_stats_p_choose_inline, yes_no_kb, settings_kb, words_goal_kb
from config import commands, MAX_PROBLEM_WORDS, buttons as btns, messages as ms, MIN_GOAL, MAX_GOAL
import random
from db import db
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State


class FSM_word(StatesGroup):
    word = State()

class FSM_settings(StatesGroup):
    settings = State()
    sure = State()
    goal_set = State()

async def start(message: types.Message):
    if not db.check_user_exists(message.from_user.id):
        db.reg_user(message.from_user.id, message.from_user.first_name)
    await message.reply(ms['welcome'].format(message.from_user.first_name, db.get_words_goal(db.get_user_id_by_tg_id(message.from_user.id))), reply_markup=main_kb, reply=False)

async def all_msgs(message: types.Message, state: FSMContext):
    text = message.text
    found = False
    for i in range(len(commands)):
        if text in commands[i]:
            await commands_func[i](message, state)
            found = True
    if not found:
        await message.reply(ms['cmd_not_found'])

async def word_cmd(message: types.Message, state: FSMContext):
    rand = random.randint(1, db.get_words_len())
    word = db.get_word(rand)
    comment = ''
    if word.comment_exists():
        comment = f"\({word.comment}\)"
    await message.reply(f'{word.value.lower()} {comment}', reply_markup=get_word_kb(word.value.lower()), reply=False)
    async with state.proxy() as data:
        data['right_word'] = word
    await FSM_word.word.set()


async def stats_cmd(message: types.Message, state: FSMContext):
    user_id = db.get_user_id_by_tg_id(message.from_user.id)
    p = [
        db.get_words_count(user_id, 2),
        round(db.get_correct_perc(user_id, 2), 3),
        '\n'.join([f"\t- {word[0]} ({word[1]})" for word in db.get_problem_words(user_id, MAX_PROBLEM_WORDS, 2)])
    ]
    answer = f"Слов: {p[0]}\nПравильность: {p[1]}%\nПроблемные слова:\n{p[2]}"
    await message.reply(answer, reply=False, reply_markup=get_stats_p_choose_inline(2))

async def settings_cmd(message: types.Message, state: FSMContext):
    await message.reply(ms['settings'], reply_markup=settings_kb, reply=False)
    await FSM_settings.settings.set()


commands_func = [word_cmd, stats_cmd, settings_cmd]

# FSM

async def get_word(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        right_word = data['right_word']
        if message.text == btns['back']:
            await message.reply(ms['menu'], reply=False, reply_markup=main_kb)
            await state.finish()
            return
        if message.text == right_word.value or message.text.lower() == right_word.value.lower():
            rand = random.randint(1, db.get_words_len())
            word = db.get_word(rand)
            right = message.text == right_word.value
            if db.check_goal(db.get_user_id_by_tg_id(message.from_user.id)):
                await message.reply(ms['goal_reach'], reply=False)
            comment = ''
            if word.comment_exists():
                comment = f"\({word.comment}\)"
            await message.reply((ms['right'].format(word.value.lower(), comment)if right else (ms['wrong'].format(right_word.value, comment, word.value.lower(), comment))), reply=False, reply_markup=get_word_kb(word.value.lower()), parse_mode="MarkdownV2")
            db.log_word_guess(db.get_user_id_by_tg_id(message.from_user.id), right_word.id, message.text, right)
            async with state.proxy() as data:
                data['right_word'] = word
            await FSM_word.word.set()
        else:
            await message.reply(ms['retry'], reply=False)
            await FSM_word.word.set()

async def settings(message: types.Message, state: FSMContext):
    if message.text == btns['reset_stats']:
        await message.reply(ms['sure'], reply=False, reply_markup=yes_no_kb)
        await FSM_settings.sure.set()
    elif message.text == btns['words_goal']:
        current_goal = db.get_words_goal(db.get_user_id_by_tg_id(message.from_user.id))
        await message.reply(ms['set_goal_input'].format(current_goal), reply=False, reply_markup=words_goal_kb, parse_mode="MarkdownV2")
        await FSM_settings.goal_set.set()
    else:
        await message.reply(ms['main_menu'], reply=False, reply_markup=main_kb)
        await state.finish()

async def yes_no_reset(message: types.Message, state: FSMContext):
    if message.text == btns['yes']:
        db.reset_stats(db.get_user_id_by_tg_id(message.from_user.id))
        await message.reply(ms['stats_reset'], reply=False, reply_markup=settings_kb)
    else:
        await message.reply(ms['cancel'], reply=False, reply_markup=settings_kb)
    await FSM_settings.settings.set()

async def words_goal(message: types.Message, state: FSMContext):
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
    db.set_words_goal(db.get_user_id_by_tg_id(message.from_user.id), message.text)
    await message.reply(ms['new_goal'], reply=False, reply_markup=settings_kb)
    await FSM_settings.settings.set()

def reg_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(all_msgs)

    #FSM
    dp.register_message_handler(get_word, state=FSM_word.word)
    dp.register_message_handler(settings, state=FSM_settings.settings)
    dp.register_message_handler(yes_no_reset, state=FSM_settings.sure)
    dp.register_message_handler(words_goal, state=FSM_settings.goal_set)