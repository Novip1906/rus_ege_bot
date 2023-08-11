from models import Stress, ProblemWords

problem_words = list()


def check_in_pwords(user_id: int):
    for word in problem_words:
        if word.user_id == user_id:
            return True
    return False

def check_pwords_empty(user_id: int):
    for word in problem_words:
        if len(word.words) == 0:
            return True
    return False

def get_pword(user_id) -> ProblemWords:
    for word in problem_words:
        if word.user_id == user_id:
            return word

def get_pword_i(user_id) -> int:
    for i in range(len(problem_words)):
        if problem_words[i].user_id == user_id:
            return i

