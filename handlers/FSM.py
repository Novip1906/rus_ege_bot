from aiogram.dispatcher.filters.state import StatesGroup, State


class FSM_stress(StatesGroup):
    word = State()

class FSM_settings(StatesGroup):
    settings = State()
    sure = State()
    goal_set = State()
    ref_link = State()

class FSM_words(StatesGroup):
    word = State()

class FSM_stress_goal(StatesGroup):
    goal = State()