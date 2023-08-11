from keyboards import get_stress_kb
from models import Word, Stress
from config import messages as ms
from aiogram import types


async def send_stress(message: types.Message, word: Stress, right_word=None):
    if right_word is None:
        comment = ''
        if word.comment_exists():
            comment = f"({word.comment})"
        ans = ms['first_word'].format('{}', comment)
        await message.answer(ans.format(word.value.lower()), reply_markup=get_stress_kb(word.value.lower()))
    else:
        right = message.text == right_word.value
        comment = ''
        new_comment = ''
        explain = ''
        if right_word.comment_exists():
            comment = f"\({right_word.comment}\)"
        if word.comment_exists():
            new_comment = f"\({word.comment}\)"
        ans = ms['right'].format(word.value.lower(), new_comment, '') if right else (
            ms['wrong'].format(right_word.value, comment, explain, word.value.lower(), new_comment, ''))
        await message.reply(ans, reply=False, reply_markup=get_stress_kb(word.value.lower()), parse_mode='MarkdownV2')
