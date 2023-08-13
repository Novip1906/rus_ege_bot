from models import Stress, ProblemWords

problem_stress = list()
problem_words = list()


def check_in_pstress(user_id: int):
    for word in problem_stress:
        if word.user_id == user_id:
            return True
    return False

def check_pstress_empty():
    for word in problem_stress:
        if len(word.words) == 0:
            return True
    return False

def get_pstress(user_id) -> ProblemWords:
    for word in problem_stress:
        if word.user_id == user_id:
            return word

def get_pstress_i(user_id) -> int:
    for i in range(len(problem_stress)):
        if problem_stress[i].user_id == user_id:
            return i

def check_in_pwords(user_id: int):
    for word in problem_words:
        if word.user_id == user_id:
            return True
    return False

def check_pwords_empty():
    for word in problem_words:
        if len(word.words) == 0:
            return True
    return False

def get_pwords(user_id) -> ProblemWords:
    for word in problem_words:
        if word.user_id == user_id:
            return word

def get_pwords_i(user_id) -> int:
    for i in range(len(problem_words)):
        if problem_words[i].user_id == user_id:
            return i




