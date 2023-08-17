from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram import Dispatcher, types
from aiogram.utils.deep_linking import get_start_link

import config
from db import db
from config import MAX_PROBLEM_WORDS, buttons as btns, messages as ms
from handlers.FSM import FSM_stress_goal, FSM_words_goal

vowels = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я']

stress_btn = KeyboardButton(btns['stress'])
words_btn = KeyboardButton(btns['words'])
profile_btn = KeyboardButton(btns['profile'])
settings_btn = KeyboardButton(btns['settings'])
reset_stats_btn = KeyboardButton(btns['reset_stats'])
words_goal_btn = KeyboardButton(btns['words_goal'])
back_btn = KeyboardButton(btns['back'])
yes_btn = KeyboardButton(btns['yes'])
no_btn = KeyboardButton(btns['no'])
get_ref_link_btn = KeyboardButton(btns['get_ref_link'])
report_btn = KeyboardButton(btns['report'])
add_word_btn = KeyboardButton(btns['add_word'])

stress_goal_inl_btn = InlineKeyboardButton(btns['stress_goal'], callback_data='settings_stress-goal')
words_goal_inl_btn = InlineKeyboardButton(btns['words_goal'], callback_data='settings_words-goal')

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(stress_btn, words_btn).add(profile_btn).row(report_btn, add_word_btn)

words_kb = ReplyKeyboardMarkup(resize_keyboard=True)
words_kb.add(back_btn)

yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True)
yes_no_kb.row(yes_btn, no_btn)

stress_goal_kb = ReplyKeyboardMarkup(resize_keyboard=True)
stress_goal_kb.row(KeyboardButton('50'), KeyboardButton('100'), KeyboardButton('200'))
stress_goal_kb.add(back_btn)

back_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(back_btn)

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)

empty_kb, empty_inl = ReplyKeyboardMarkup(), InlineKeyboardMarkup()

channel_link_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('Наш канал', url=config.sub_channel_link))

check_for_sub_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(btns['check']))


def get_settings_inl_kb(sub_active):
    settings_inl_kb = InlineKeyboardMarkup(resize_keyboard=True)
    if sub_active:
        settings_inl_kb.add(InlineKeyboardButton(btns['reset_stats'], callback_data='settings_reset-stats'))
    settings_inl_kb.add(stress_goal_inl_btn)
    settings_inl_kb.add(words_goal_inl_btn)
    settings_inl_kb.add(InlineKeyboardButton(btns['back'], callback_data='profile_main'))
    return settings_inl_kb

def get_stress_kb(word: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(word)):
        if word[i] in vowels:
            tmp_word = list(word)
            tmp_word[i] = word[i].upper()
            kb.add(KeyboardButton(''.join(tmp_word)))
    kb.add(back_btn)
    return kb


def get_profile_inline(sub_active) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(btns['stats'].format('📈' if sub_active else '🔒'), callback_data=f'stats{1 if sub_active else 0}'))
    if (sub_active):
        kb.add(InlineKeyboardButton(btns['prolong_sub'], callback_data='sub1'))
    else:
        kb.add(InlineKeyboardButton(btns['buy_sub'], callback_data='sub0'))
    kb.add(InlineKeyboardButton(btns['ref_link'], callback_data='ref_link'))
    kb.add(InlineKeyboardButton(btns['settings'], callback_data='settings_main'))
    kb.add()
    return kb

def get_sub_price_kb(balance):
    _, periods, prices = config.PRICES
    kb = InlineKeyboardMarkup()
    print(periods, prices)
    for i in range(len(prices)):
        kb.add(InlineKeyboardButton(f"{periods[i]} ({prices[i]}₽) {'✅' if prices[i] <= balance else '❌'}",
                                    callback_data=f'price{i}'))
    kb.add(InlineKeyboardButton(btns['back'], callback_data='profile_main'))
    return kb
async def sub_handler(query: types.CallbackQuery):
    status = query.data[-1]
    balance = db.users.get_balance(query.from_user.id)
    if status == '0':
        await query.message.edit_text(ms['sub_info'].format(balance), reply_markup=get_sub_price_kb(balance), parse_mode=ParseMode.HTML)
    else:
        sub_end = db.users.get_sub_end(query.from_user.id)
        await query.message.edit_text(ms['sub_info'].format(balance) + '\n' + ms['sub_end'].format(sub_end),
                                      reply_markup=get_sub_price_kb(balance), parse_mode=ParseMode.HTML)

async def price_handler(query: types.CallbackQuery):
    i = int(query.data[-1])
    days, _, prices = config.PRICES
    day, price = days[i], prices[i]
    balance = db.users.get_balance(query.from_user.id)
    if price > balance:
        await query.answer(ms['not_enough_balance'])
        return
    end = db.users.add_sub(query.from_user.id, day)
    db.users.remove_money(query.from_user.id, price)
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton(btns['to_profile'], callback_data='profile_main'))
    await query.message.edit_text(ms['bought'].format(end), reply_markup=kb, parse_mode=ParseMode.HTML)

def get_stats_p_choose_inline(current: int):
    stats_period_choose_inline = InlineKeyboardMarkup()
    period_names = ['Всё время', 'Месяц', 'Сегодня']
    for i in 2, 1, 0:
        stats_period_choose_inline.add(
            InlineKeyboardButton(period_names[i] + (' ✅' if current == i else ''), callback_data=f'period{i}'))
    stats_period_choose_inline.add(InlineKeyboardButton(btns['back'], callback_data='profile_main'))
    return stats_period_choose_inline


async def stats_callback(query: types.CallbackQuery):
    sub_active = query.data[-1] == '1'
    user_id = db.users.get_by_tg(query.from_user.id)
    if sub_active:
        pstress = '\n'.join([f"\t- {word[0]} ({word[1]})" for word in db.stress.get_problem_words(user_id, MAX_PROBLEM_WORDS, 2)])
        pwords = '\n'.join([f"\t- {word[0]} ({word[1]})" for word in db.words.get_problem_words(query.from_user.id, MAX_PROBLEM_WORDS, 2)])
        if len(pstress) == 0:
            pstress = 'Таких нет 😄'
        if len(pwords) == 0:
            pwords = 'Таких нет 😁'
        p = [
            db.stress.get_words_count(user_id, 2),
            round(db.stress.get_correct_perc(user_id, 2), 3),
            pstress,
            db.words.get_words_count(query.from_user.id, 2),
            round(db.words.get_correct_perc(query.from_user.id, 2), 3),
            pwords
        ]
        answer = ms['stats_body'].format(p[0], p[1], p[2], p[3], p[4], p[5])
        await query.message.edit_text(answer, reply_markup=get_stats_p_choose_inline(2), parse_mode=ParseMode.HTML)
    else:
        await query.answer(text="Оформите подписку, чтобы видеть статистику!")

async def ref_link_callback(query: types.CallbackQuery):
    ref_link = await get_start_link(str(query.from_user.id), encode=True)
    back_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(btns['back'], callback_data='profile_main'))
    await query.message.edit_text(ms['ref_link'].format(ref_link), parse_mode=ParseMode.HTML, reply_markup=back_kb)

async def profile_handler(query: types.CallbackQuery):
    status = query.data.split('_')[1]
    if status == 'main':
        await show_profile(query.message, True, query.from_user.id)

async def process_stats_period_choose_callback(query: types.CallbackQuery):
    period = query.data[-1]
    user_id = db.users.get_by_tg(query.from_user.id)
    if period.isdigit():
        period = int(period)
    pstress = '\n'.join(
        [f"\t- {word[0]} ({word[1]})" for word in db.stress.get_problem_words(user_id, MAX_PROBLEM_WORDS, 2)])
    pwords = '\n'.join(
        [f"\t- {word[0]} ({word[1]})" for word in db.words.get_problem_words(query.from_user.id, MAX_PROBLEM_WORDS, 2)])
    if len(pstress) == 0:
        pstress = 'Таких нет 😄'
    if len(pwords) == 0:
        pwords = 'Таких нет 😁'
    p = [
        db.stress.get_words_count(user_id, period),
        round(db.stress.get_correct_perc(user_id, period), 3),
        pstress,
        db.words.get_words_count(query.from_user.id, period),
        round(db.words.get_correct_perc(query.from_user.id, period), 3),
        pwords
    ]
    answer = ms['stats_body'].format(p[0], p[1], p[2], p[3], p[4], p[5])
    await query.message.edit_text(answer, reply_markup=get_stats_p_choose_inline(period), parse_mode=ParseMode.HTML)

async def show_profile(message: types.Message, edit: bool, tg_id):
    user_id = db.users.get_by_tg(tg_id)
    balance = db.users.get_balance(tg_id)
    sub_status = db.users.check_sub(tg_id)
    referals = db.users.get_refs_count(tg_id)
    sub_ans = f'<b>Активна</b> ✅ (до {db.users.get_sub_end(tg_id)})' if sub_status else '<b>Неактивна</b> ❌'
    if edit:
        await message.edit_text(ms['profile'].format(balance, sub_ans, referals), parse_mode=ParseMode.HTML, reply_markup=get_profile_inline(sub_status))
    else:
        await message.answer(ms['profile'].format(balance, sub_ans, referals), parse_mode=ParseMode.HTML, reply_markup=get_profile_inline(sub_status))

async def settings_callback(query: types.CallbackQuery):
    status = query.data.split('_')[1]
    if status == 'main':
        await query.message.edit_text(ms['settings'], reply_markup=get_settings_inl_kb(db.users.check_sub(query.from_user.id)))
    elif status == 'stress-goal':
        current_goal = db.stress.get_words_goal(db.users.get_by_tg(query.from_user.id))
        await query.message.answer(ms['set_goal_input'].format(current_goal), reply_markup=stress_goal_kb,
                                   parse_mode="MarkdownV2")
        await FSM_stress_goal.goal.set()
    elif status == 'words-goal':
        current_goal = db.words.get_words_goal(query.from_user.id)
        await query.message.answer(ms['set_goal_input'].format(current_goal), reply_markup=stress_goal_kb,
                                   parse_mode="MarkdownV2")
        await FSM_words_goal.goal.set()
    elif status == 'reset-stats':
        yes_inl = InlineKeyboardButton(btns['yes'], callback_data='reset-stats_yes')
        no_inl = InlineKeyboardButton(btns['no'], callback_data='reset-stats_no')
        kb = InlineKeyboardMarkup().row(yes_inl, no_inl)
        await query.message.edit_text(ms['sure'], reply_markup=kb)

async def reset_stats(query: types.CallbackQuery):
    ans = query.data.split('_')[1]
    if ans == 'yes':
        db.stress.reset_stats(db.users.get_by_tg(query.from_user.id))
        await query.message.edit_text(ms['stats_reset'] + '\n\n' + ms['settings'], reply_markup=get_settings_inl_kb(True))
    else:
        await query.message.edit_text(ms['settings'], reply_markup=get_settings_inl_kb(True))

def admin_get_new_word_kb_word() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(btns['reject'])).add(back_btn)

def admin_get_new_word_kb_correct(correct: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(correct)).add(back_btn)

def admin_get_new_word_kb_comment() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(btns['skip'])).add(back_btn)

def reg_inline_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_stats_period_choose_callback, text_startswith='period')
    dp.register_callback_query_handler(stats_callback, text_startswith='stats')
    dp.register_callback_query_handler(ref_link_callback, text_startswith='ref_link')
    dp.register_callback_query_handler(profile_handler, text_startswith='profile')
    dp.register_callback_query_handler(settings_callback, text_startswith='settings')
    dp.register_callback_query_handler(reset_stats, text_startswith='reset-stats')
    dp.register_callback_query_handler(sub_handler, text_startswith='sub')
    dp.register_callback_query_handler(price_handler, text_startswith='price')