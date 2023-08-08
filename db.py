import sqlite3
from models import Word
from datetime import datetime, timedelta

DB_DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"

def current_datetime():
    return datetime.now().strftime(DB_DATETIME_FORMAT)

class DB:
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cur = self.conn.cursor()
            print("База данных подключена")

        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)

    def write_words(self, words: list, rewrite: bool):
        if rewrite:
            self.cur.execute(f"DELETE FROM words")
            for word in words:
                self.cur.execute(f"INSERT INTO words (word) VALUES ('{word}')")
                self.conn.commit()
            return
        for word in words:
            self.cur.execute(f"SELECT * FROM words WHERE word='{word}'")
            res = self.cur.fetchall()
            if len(res) > 0:
                continue
            self.cur.execute(f"INSERT INTO words (word) VALUES ('{word}')")
            self.conn.commit()

    def get_words_len(self):
        self.cur.execute("SELECT COUNT(*) FROM words")
        return self.cur.fetchall()[0][0]

    def get_word(self, id: int) -> Word:
        self.cur.execute(f"SELECT * FROM words WHERE id={id}")
        r = self.cur.fetchall()
        if len(r) == 0:
            return None
        return Word(id, r[0][1], r[0][2])

    def check_user_exists(self, tg_id) -> bool:
        self.cur.execute(f"SELECT * FROM users WHERE tg_id='{tg_id}'")
        return len(self.cur.fetchall()) > 0

    def reg_user(self, tg_id, first_name):
        self.cur.execute(f"INSERT INTO users (tg_id, first_name, create_datetime) VALUES ('{tg_id}', '{first_name}', '{current_datetime()}')")
        self.conn.commit()

    def log_word_guess(self, user_id, right_word_id, word, guessed):
        self.cur.execute(f"INSERT INTO word_guess_logs (user_id, right_word_id, word, datetime, guessed) VALUES ('{user_id}', '{right_word_id}', '{word}', '{current_datetime()}', '{1 if guessed else 0}')")
        self.conn.commit()

    def get_user_id_by_tg_id(self, tg_id):
        self.cur.execute(f"SELECT id FROM users WHERE tg_id='{tg_id}'")
        return self.cur.fetchall()[0][0]

    # periods:
    # 0 - all time
    # 1 - month
    # 2 - today

    def get_word_guess_logs_by_period(self, user_id, period) -> list:
        self.cur.execute(f"SELECT * FROM word_guess_logs WHERE user_id={user_id} AND include_in_stats=1")
        logs = self.cur.fetchall()
        if period == 0:
            return logs
        if period == 1:
            one_month_ago = (datetime.now() - timedelta(days=30)).date()
            return [log for log in logs if datetime.strptime(log[5], DB_DATETIME_FORMAT).date() >= one_month_ago]
        if period == 2:
            today = datetime.now().date()
            return [log for log in logs if datetime.strptime(log[5], DB_DATETIME_FORMAT).date() == today]

    def get_correct_perc(self, user_id, period) -> float:
        logs = self.get_word_guess_logs_by_period(user_id, period)
        right = len([log for log in logs if log[4] == 1])
        if len(logs) == 0:
            return 0
        return (right / len(logs)) * 100

    def get_problem_words(self, user_id, max_words, period):
        logs = self.get_word_guess_logs_by_period(user_id, period)
        words = dict()
        for log in logs:
            word_id, correct = log[2], log[4] == 1
            if correct:
                continue
            if word_id in words:
                words[word_id] += 1
            else:
                words[word_id] = 1
        ids = sorted(words, reverse=True, key=lambda x: words[x])
        res = [(self.get_word(id).value, words[id]) for id in ids]
        if len(ids) < max_words:
            return res
        return res[:max_words] #(value, mistakes)


    def reset_stats(self, user_id):
        self.cur.execute(f"UPDATE word_guess_logs SET include_in_stats=0 WHERE user_id={user_id}")
        self.conn.commit()

    def get_words_count(self, user_id, period) -> int:
        logs = self.get_word_guess_logs_by_period(user_id, period)
        return len(logs)

    def get_words_goal(self, user_id):
        self.cur.execute(f"SELECT words_goal FROM users WHERE id={user_id}")
        return self.cur.fetchall()[0][0]

    def set_words_goal(self, user_id, goal):
        self.cur.execute(f"UPDATE users SET words_goal={goal} WHERE id={user_id}")
        self.conn.commit()

    def check_goal(self, user_id):
        logs = self.get_word_guess_logs_by_period(user_id, 2)
        return len(logs) == db.get_words_goal(user_id)

    def get_all_users(self) -> list:
        self.cur.execute(f"SELECT * FROM users")
        return self.cur.fetchall()

db = DB('database.db')
