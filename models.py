from dataclasses import dataclass


@dataclass
class Word:
    id: int
    value: str
    comment: str

    def comment_exists(self):
        return self.comment is not None
