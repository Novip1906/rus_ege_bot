TG_TOKEN = '6427428832:AAELKb7ZIQ4OgVl01oW5mMEv_Xz3y3I7BDw'

TG_TOKEN_TEST = '6368744766:AAGH5KU4Q-T8_7Y4d8uevMKQ6iA7KJJFXS8'
TEST = True

DB_PATH = '/Users/philippschepnov/PycharmProjects/rus_ege_stress_bot/database.db'

MAX_PROBLEM_WORDS = 5
MIN_GOAL, MAX_GOAL = 10, 20000
SHOW_SUBSCR_AD = 5
RANDOM_INTERVAL = 10
SHOW_WORD_REPORT = True

MONEY_FOR_REFERAL = 8
MONEY_FOR_WORD = 5

REPORT_MAX_LEN = 150
COMMENT_MAX_LEN = 20
EXPLAIN_MAX_LEN = 70

sub_channel = '-1001917694850'
sub_channel_link = 'https://t.me/ege_stress'

PRICES = [30, 60, 90], ['1 месяц', '2 месяца', '3 месяца'], [59, 99, 149]

emoji = '😃😄😁😆☺️😊🙂😉😌'

buttons = {
    'stress': 'Ударения 💬',
    'words': 'Слова 💬',
    'profile': 'Профиль 👀',
    'reset_stats': 'Сбросить статистику 🔄',
    'stress_goal': 'Цель по ударениям 💡',
    'words_goal': 'Цель по словам 🎯',
    'settings': 'Настройки ⚙️',
    'back': 'Назад ↩️',
    'yes': 'Да ✅',
    'no': 'Нет ❌',
    'get_ref_link': 'Реферальная ссылка ✉️',
    'stats': 'Статистика {}',
    'buy_sub': 'Купить подписку 💡',
    'prolong_sub': 'Продлить подписку 🕒',
    'ref_link': 'Реферальная ссылка 🔗',
    'to_profile': 'В профиль ↩️',
    'add_word': 'Добавить слово 💰',
    'report': 'Репорт 🆘',
    'reject': 'Отклонить',
    'skip': 'Пропустить',
    'sub_ad': '🔓Оформить подписку',
    'check': 'Проверить ✅',
    'get_qr': 'Получить QR-код 📸'
}

commands = [
    [buttons['stress']],
    [buttons['words']],
    [buttons['profile']],
    [buttons['report']],
    [buttons['add_word']],
    [buttons['back']]
]

messages = {
    'join_channel': 'Для начала подпишитесь на наш канал 😉',
    'join_channel2': 'После этого нажмите кнопку для проверки ✅',
    'not_subscribed': 'Вы не подписались 😔',
    'welcome': 'Добро пожаловать, {}! 👋\nВаша цель: {} слов\n\n{}',
    'cmd_not_found': 'Команда не найдена ❌',
    'settings': 'Настройки ⚙️',
    'menu': 'Главное меню 🏠',
    'first_word': 'Начнем {}\n\n<b>{}</b> {}',
    'right': 'Правильно ✅\n\nСледующее слово: <b>{}</b> {}\n{}',
    'wrong': 'Ошибка ❌\nПравильно: {} {}\n{}\n➡️Следующее слово: <b>{}</b> {}\n{}',
    'retry': 'Попробуйте снова 🔄',
    'sure': 'Вы уверены? 🤔',
    'main_menu': 'Главное меню',
    'stats_reset': 'Статистика обнулена 🔄',
    'cancel': 'Отмена ↩️',
    'set_goal_input': 'Ваша текущая цель: *{}* слов\nВведите новую цель 💬',
    'new_goal': 'Новая цель установлена ✅',
    'wrong_new_goal': f'💡\nМинимальная цель: {MIN_GOAL} слов\nМаксимальная: {MAX_GOAL} слов',
    'goal_reach': 'Достигнута дневная цель! Так держать! 👍',
    'sub_ad': '🔓Оформите подписку, чтобы видеть пояснения к ответам',
    'profile': """👋 <b>Ваш профиль</b>
    
💰 Баланс: {}₽
💡 Подписка: {}

👱‍ Рефералы: {} чел.
    """,
    'ref_link': '<b>🤝 Ваша реферальная ссылка:</b>\n\n<i>{}</i>',
    'add_money_for_ref': '❗️У вас новый реферал (+{}₽)\n🤝Благодарим за сотрудничество\n\n💰<b>Баланс</b>: {}₽',
    'add_money_for_word': '❗️Ваше слово "{}" одобрено (+{}₽)\n🤝Благодарим за сотрудничество\n\n💰<b>Баланс</b>: {}₽',
    'stats_body': """
<b>Ударения</b>:
Слов: {}
Правильность: {}%
Проблемные слова:
{}

<b>Слова</b>:
Слов: {}
Правильность: {}%
Проблемные слова:
{}""",
    'sub_info': """
<b>01helper Premium</b>

<b>Преимущества</b>:
\t✅\tПросмотр статистики 📈
\t✅\tУмный алгоритм подбора слов 🧠
\t✅\tПросмотр пояснения к словам 💬

💰 Ваш баланс: {}₽
""",
    'not_enough_balance': 'Недостаточно средств ❌',
    'bought': '🥳 <b>Поздравляем с покупкой!</b>\n\nВаша подписка доступна до {}',
    'sub_end': '💡 Ваша подписка активна до {}',
    'add_word_info': f"""<b>Добавление слов</b>
ℹ️\tВы можете помочь боту, добавив в его базу данных новые слова

💬\tЗа каждое добавленное слово вы будете получать {MONEY_FOR_WORD}₽!

Введите правильное слово...
""",
    'add_word_with_space': 'Отлично✅\n\nТеперь введите слово с пропуском💬\nНапример: вым_кнуть',
    'add_word_comment': """
Теперь введите комментарий к слову💬
Например: под дождем (Вымокнуть под дождем, поэтому "под дождем" - комментарий)

Если комментарий не нужен, пропустите его ✅""",
    'add_word_comment_max_len': f'💡Максимальная длина комментария: {COMMENT_MAX_LEN}\n\nПопробуйте снова...',
    'add_word_explain': """Напишите объяснение, то есть почему слово пишется так 🤔

💬Пример к слову вымокнуть: в словах со значением «пропускать жидкость» пишется корень МОК
""",
    'add_word_explain_max_len': f'💡Максимальная длина пояснения: {EXPLAIN_MAX_LEN}\n\nПопробуйте снова...',
    'add_word_exists': 'Такое слово уже существует :( ❌\n\nПопробуйте снова...',
    'add_word_new_exists': 'Вы уже отправляли это слово ❌\n\nПопробуйте слова...',
    'add_word_to_approve': 'Слово отправлено на одобрение ✅\n\nОжидайте 🕒\nВведите правильное слово...',
    'report_info': """💬Напишите ваш вопрос, предложение или жалобу.""",
    'report_answer': '❗<b>Ответ на репорт</b>:\n\n{}',
    'report_max_len': f'💡Максимальная длина: {REPORT_MAX_LEN}',
    'report_sent': 'Репорт отправлен ✅\n\nНаши модераторы вам скоро ответят на него {}',
    'banned': 'Вы заблокированы ❌',
    'unbanned': 'Вы разблокированы ✅',
    'admin_msg': '❗️Сообщение от администратора:\n\n{}',
    'word_report_sent': 'Сообщение об ошибке отправлено✅'
}

admin_messages = {
    'add_word': """
ОДОБРЕНИЕ СЛОВА
id: {}
tg_id: {}
слово: {}    
""",
    'report': """
РЕПОРТ
id: {}
tg_id: {}
текст: {} 
""",
    'word_report': "РЕПОРТ НА СЛОВО:\nЮзер: {}\n\n{}"
}
