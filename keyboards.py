from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram import Dispatcher, types
from aiogram.utils.deep_linking import get_start_link
from db import db
from config import MAX_PROBLEM_WORDS, buttons as btns, messages as ms

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

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(stress_btn, words_btn).add(profile_btn)

words_kb = ReplyKeyboardMarkup(resize_keyboard=True)
words_kb.add(back_btn)

yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True)
yes_no_kb.row(yes_btn, no_btn)

settings_kb = ReplyKeyboardMarkup(resize_keyboard=True)
settings_kb.row(reset_stats_btn, words_goal_btn)
settings_kb.add(get_ref_link_btn)
settings_kb.add(back_btn)

stress_goal_kb = ReplyKeyboardMarkup(resize_keyboard=True)
stress_goal_kb.row(KeyboardButton('50'), KeyboardButton('100'), KeyboardButton('200'))
stress_goal_kb.add(back_btn)


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
    return kb


def get_stats_p_choose_inline(current: int):
    stats_period_choose_inline = InlineKeyboardMarkup()
    period_names = ['Всё время', 'Месяц', 'Сегодня']
    for i in 2, 1, 0:
        stats_period_choose_inline.add(
            InlineKeyboardButton(period_names[i] + (' ✅' if current == i else ''), callback_data=f'period{i}'))
    stats_period_choose_inline.add(InlineKeyboardButton(btns['back'], callback_data='profile_main'))
    return stats_period_choose_inline


async def stats_callback(callback_query: types.CallbackQuery):
    sub_active = callback_query.data[-1] == '1'
    user_id = db.users.get_by_tg(callback_query.from_user.id)
    if sub_active:
        pwords = '\n'.join([f"\t- {word[0]} ({word[1]})" for word in db.stress.get_problem_words(user_id, MAX_PROBLEM_WORDS, 2)])
        if len(pwords) == 0:
            pwords = 'Таких нет 😄'
        p = [
            db.stress.get_words_count(user_id, 2),
            round(db.stress.get_correct_perc(user_id, 2), 3),
            pwords
        ]
        answer = f"Слов: {p[0]}\nПравильность: {p[1]}%\nПроблемные слова:\n{p[2]}"
        await callback_query.message.edit_text(answer, reply_markup=get_stats_p_choose_inline(2))
    else:
        await callback_query.answer(text="Оформите подписку, чтобы видеть статистику!")

async def ref_link_callback(query: types.CallbackQuery):
    ref_link = await get_start_link(str(db.users.get_by_tg(query.from_user.id)), encode=True)
    back_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(btns['back'], callback_data='profile_main'))
    await query.message.edit_text(ms['ref_link'].format(ref_link), parse_mode=ParseMode.HTML, reply_markup=back_kb)

async def profile_handler(query: types.CallbackQuery):
    status = query.data.split('_')[1]
    if status == 'main':
        await show_profile(query.message, True, query.from_user.id)

async def process_stats_period_choose_callback(callback_query: types.CallbackQuery):
    period = callback_query.data[-1]
    user_id = db.users.get_by_tg(callback_query.from_user.id)
    if period.isdigit():
        period = int(period)
    pwords = '\n'.join(
        [f"\t- {word[0]} ({word[1]})" for word in db.stress.get_problem_words(user_id, MAX_PROBLEM_WORDS, 2)])
    if len(pwords) == 0:
        pwords = 'Таких нет 😄'
    p = [
        db.stress.get_words_count(user_id, period),
        round(db.stress.get_correct_perc(user_id, period), 3),
        pwords
    ]
    answer = f"Слов: {p[0]}\nПравильность: {p[1]}%\nПроблемные слова:\n{p[2]}"
    await callback_query.message.edit_text(answer, reply_markup=get_stats_p_choose_inline(period))

async def show_profile(message: types.Message, edit: bool, tg_id):
    user_id = db.users.get_by_tg(tg_id)
    balance = db.users.get_balance(user_id)
    sub_status = db.users.check_sub(user_id)
    referals = db.users.get_refs_count(user_id)
    sub_ans = f'<b>Активна</b> ✅ (до {db.users.get_sub_end(user_id)})' if sub_status else '<b>Неактивна</b> ❌'
    if edit:
        await message.edit_text(ms['profile'].format(balance, sub_ans, referals), parse_mode=ParseMode.HTML, reply_markup=get_profile_inline(sub_status))
    else:
        await message.answer(ms['profile'].format(balance, sub_ans, referals), parse_mode=ParseMode.HTML, reply_markup=get_profile_inline(sub_status))

def reg_inline_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_stats_period_choose_callback, text_startswith='period')
    dp.register_callback_query_handler(stats_callback, text_startswith='stats')
    dp.register_callback_query_handler(ref_link_callback, text_startswith='ref_link')
    dp.register_callback_query_handler(profile_handler, text_startswith='profile')
