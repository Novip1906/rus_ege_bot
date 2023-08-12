from models import Stress, ProblemWords

problem_stress = list()


def check_in_pstress(user_id: int):
    for word in problem_stress:
        if word.user_id == user_id:
            return True
    return False

def check_pstress_empty(user_id: int):
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

