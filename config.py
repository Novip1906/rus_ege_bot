TG_TOKEN = '6678292463:AAG2dQ2HWJUVeRJhUbsENEpBzEOF9O5oM7Y'

TG_TOKEN_TEST = '6368744766:AAGH5KU4Q-T8_7Y4d8uevMKQ6iA7KJJFXS8'
TEST = True

MAX_PROBLEM_WORDS = 8
MIN_GOAL, MAX_GOAL = 10, 20000

commands = [
    ['Ударения 💬'],
    ['Слова 💬'],
    ['Статистика 📈'],
    ['Настройки ⚙️']
]

buttons = {
    'stress': 'Ударения 💬',
    'words': 'Слова 💬',
    'stats': 'Статистика 📈',
    'reset_stats': 'Сбросить статистику 🔄',
    'words_goal': 'Дневная цель 💡',
    'settings': 'Настройки ⚙️',
    'back': 'Назад ↩️',
    'yes': 'Да ✅',
    'no': 'Нет ❌'
}

messages = {
    'welcome': 'Добро пожаловать, {}! 👋\nВаша цель: {} слов',
    'cmd_not_found': 'Команда не найдена ❌',
    'settings': 'Настройки ⚙️',
    'menu': 'Главное меню',
    'first_word': '{} {}',
    'right': 'Правильно ✅\n\nСледующее слово: *{}* {}',
    'wrong': 'Ошибка ❌\nПравильно: {} {}\n{}\nСледующее слово: *{}* {}',
    'retry': 'Попробуйте снова 🔄',
    'sure': 'Вы уверены? 🤔',
    'main_menu': 'Главное меню',
    'stats_reset': 'Статистика обнулена 🔄',
    'cancel': 'Отмена ↩️',
    'set_goal_input': 'Ваша текущая цель: *{}* слов\nВведите новую цель 💬',
    'new_goal': 'Новая цель установлена ✅',
    'wrong_new_goal': f'💡\nМинимальная цель: {MIN_GOAL} слов\nМаксимальная: {MAX_GOAL} слов',
    'goal_reach': 'Достигнута дневная цель! Так держать! 👍'
}
