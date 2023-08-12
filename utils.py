from aiogram.types import ParseMode

from keyboards import get_stress_kb, words_kb
from models import Word, Stress
from config import messages as ms
from aiogram import types
from db import db

def check_for_mkv2(text: str) -> str:
    if '_' in text:
        i = text.index('_')
        return text[:i] + "\\" + text[i:]
    return text

async def send_stress(message: types.Message, word, isStress: bool, right_word=None):
    if right_word is None:
        comment = ''
        if word.comment_exists():
            comment = f"({word.comment})"
        value = word.value.lower() if isStress else word.value
        markup = get_stress_kb(word.value.lower()) if isStress else words_kb
        ans = ms['first_word'].format(value, comment)
        await message.answer(ans, reply_markup=markup)
    else:
        user_id = db.users.get_by_tg(message.from_user.id)
        right = message.text == right_word.value
        if not isStress:
            right = message.text.lower().replace('ё', 'е') == right_word.correct.lower().replace('ё', 'е')
        comment = ''
        new_comment = ''
        explain = 'Пояснение: 🔒\n'
        sub_ad = ''
        if right_word.comment_exists():
            comment = f"\({right_word.comment}\)"
        if word.comment_exists():
            new_comment = f"\({word.comment}\)"
        if not Stress:
            if db.users.check_sub_ad(user_id):
                sub_ad = f'\n{ms["sub_ad"]}'
        value = word.value.lower() if isStress else word.value
        value = check_for_mkv2(value)
        markup = get_stress_kb(word.value.lower()) if isStress else words_kb
        ans = ms['right'].format(value, new_comment, '') if right else (
            ms['wrong'].format(right_word.value if isStress else check_for_mkv2(right_word.correct), comment, explain, value, new_comment, sub_ad))
        await message.reply(ans, reply=False, reply_markup=markup, parse_mode='MarkdownV2')

