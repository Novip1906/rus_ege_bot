from dataclasses import dataclass


@dataclass
class Stress:
    id: int
    value: str
    comment: str

    def comment_exists(self):
        return self.comment is not None


@dataclass
class Word:
    id: int
    value: str
    correct: str
    comment: str
    explain: str = ''

    def comment_exists(self):
        return self.comment is not None and self.comment != ''


@dataclass
class ProblemWords:
    user_id: int
    words: set
