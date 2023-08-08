from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Dispatcher, types
from db import db
from config import MAX_PROBLEM_WORDS, buttons as btns

vowels = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я']

word_btn = KeyboardButton(btns['word'])
stats_btn = KeyboardButton(btns['stats'])
settings_btn = KeyboardButton(btns['settings'])
reset_stats_btn = KeyboardButton(btns['reset_stats'])
words_goal = KeyboardButton(btns['words_goal'])
back_btn = KeyboardButton(btns['back'])
yes_btn = KeyboardButton(btns['yes'])
no_btn = KeyboardButton(btns['no'])

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(word_btn).row(stats_btn, settings_btn)

yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True)
yes_no_kb.row(yes_btn, no_btn)

settings_kb = ReplyKeyboardMarkup(resize_keyboard=True)
settings_kb.add(reset_stats_btn)
settings_kb.add(words_goal)
settings_kb.add(back_btn)

words_goal_kb = ReplyKeyboardMarkup(resize_keyboard=True)
words_goal_kb.row(KeyboardButton('50'), KeyboardButton('100'), KeyboardButton('200'))
words_goal_kb.add(back_btn)
def get_word_kb(word: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(word)):
        if word[i] in vowels:
            tmp_word = list(word)
            tmp_word[i] = word[i].upper()
            kb.add(KeyboardButton(''.join(tmp_word)))
    kb.add(back_btn)
    return kb

def get_stats_p_choose_inline(current: int):
    stats_period_choose_inline = InlineKeyboardMarkup()
    period_names = ['Всё время', 'Месяц', 'Сегодня']
    for i in 2, 1, 0:
        stats_period_choose_inline.add(InlineKeyboardButton(period_names[i] + (' ✅' if current == i else ''), callback_data=f'period{i}'))
    return stats_period_choose_inline

async def process_stats_period_choose_callback(callback_query: types.CallbackQuery):
    period = callback_query.data[-1]
    user_id = db.get_user_id_by_tg_id(callback_query.from_user.id)
    if period.isdigit():
        period = int(period)
    p = [
        db.get_words_count(user_id, period),
        round(db.get_correct_perc(user_id, period), 3),
        '\n'.join([f"\t- {word[0]} ({word[1]})" for word in db.get_problem_words(user_id, MAX_PROBLEM_WORDS, period)])
    ]
    answer = f"Слов: {p[0]}\nПравильность: {p[1]}%\nПроблемные слова:\n{p[2]}"
    await callback_query.message.edit_text(answer)
    await callback_query.message.edit_reply_markup(get_stats_p_choose_inline(period))


def reg_inline_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(process_stats_period_choose_callback, text_startswith='period')

