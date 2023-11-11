import random

from aiogram.types import ParseMode

import config
from create_bot import bot
from keyboards import get_stress_kb, words_kb, get_word_report_kb
from models import Word, Stress
from config import messages as ms, MONEY_FOR_REFERAL
from aiogram import types
from db import db
from handlers.FSM import FSM_sub_channel

def check_for_mkv2(text: str) -> str:
    if '_' in text:
        i = text.index('_')
        return text[:i] + "\\" + text[i:]
    return text

async def send_word(message: types.Message, word, isStress: bool, right_word=None):
    if right_word is None:
        comment = ''
        if word.comment_exists():
            comment = f"({word.comment})"
        value = word.value.lower() if isStress else word.value
        markup = get_stress_kb(word.value.lower()) if isStress else words_kb
        ans = ms['first_word'].format(get_random_emoji(), value, comment)
        await message.answer(ans, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        user_id = db.users.get_by_tg(message.from_user.id)
        right = message.text == right_word.value
        if not isStress:
            right = message.text.lower().replace('ё', 'е') == right_word.correct.lower().replace('ё', 'е')
        comment = ''
        new_comment = ''
        explain = 'Пояснение: ' if not isStress else ''
        sub_ad = ''
        markup = get_stress_kb(word.value.lower()) if isStress else words_kb
        if right_word.comment_exists():
            comment = f"({right_word.comment})"
        if word.comment_exists():
            new_comment = f"({word.comment})"
        if not isStress and not right:
            if db.users.check_sub_ad(message.from_user.id) and not db.users.check_sub(message.from_user.id):
                sub_ad = f'\n{ms["sub_ad"]}'
            if db.users.check_sub(message.from_user.id):
                explain += right_word.explain + '\n'
            else:
                explain += '🔒\n'
            markup = get_word_report_kb(message.text)
        value = word.value.lower() if isStress else word.value
        ans = ms['right'].format(value, new_comment, '') if right else (
            ms['wrong'].format(right_word.value if isStress else right_word.correct, comment, explain, value, new_comment, sub_ad))
        await message.answer(ans, reply_markup=markup, parse_mode=ParseMode.HTML)

async def notify_about_ref(tg_id):
    balance = db.users.get_balance(tg_id)
    await bot.send_message(int(tg_id), ms['add_money_for_ref'].format(MONEY_FOR_REFERAL, balance), parse_mode=ParseMode.HTML)

async def send_message_to_admin(text):
    admins = db.admin.get_admins(1)
    for tg_id in admins:
        try:
            await bot.send_message(tg_id, text)
        except:
            pass

async def notify_about_approve(tg_id, word):
    balance = db.users.get_balance(tg_id)
    await bot.send_message(tg_id, ms['add_money_for_word'].format(word, config.MONEY_FOR_WORD, balance), parse_mode=ParseMode.HTML)

async def report_answer(tg_id, text):
    await bot.send_message(tg_id, ms['report_answer'].format(text), parse_mode=ParseMode.HTML)

async def check_sub_channel(tg_id):
    member = await bot.get_chat_member(chat_id=config.sub_channel, user_id=tg_id)
    return member['status'] != 'left'

def get_random_emoji() -> str:
    rand = random.randint(0, len(config.emoji) - 2)
    return config.emoji[rand]
