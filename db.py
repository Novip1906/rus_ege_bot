import sqlite3
from models import Stress, Word
from datetime import datetime, timedelta
from config import SHOW_SUBSCR_AD, RANDOM_INTERVAL

DB_DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"


def current_datetime():
    return datetime.now().strftime(DB_DATETIME_FORMAT)


class DB:
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cur = self.conn.cursor()
            self.stress = self._Stress(self.conn)
            self.users = self._Users(self.conn)
            self.words = self._Words(self.conn)
            print("База данных подключена")

        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)

    class _Stress:
        def __init__(self, conn):
            self.conn = conn
            self.cur = self.conn.cursor()

        def write_words(self, words: list, rewrite: bool):
            if rewrite:
                self.cur.execute(f"DELETE FROM stress")
                for word in words:
                    self.cur.execute(f"INSERT INTO stress (word) VALUES ('{word}')")
                    self.conn.commit()
                return
            for word in words:
                self.cur.execute(f"SELECT * FROM stress WHERE word='{word}'")
                res = self.cur.fetchall()
                if len(res) > 0:
                    continue
                self.cur.execute(f"INSERT INTO stress (word) VALUES ('{word}')")
                self.conn.commit()

        def log_word_guess(self, user_id, right_word_id, word, guessed):
            self.cur.execute(
                f"INSERT INTO stress_guess_logs (user_id, right_word_id, word, datetime, guessed) VALUES ('{user_id}', '{right_word_id}', '{word}', '{current_datetime()}', '{1 if guessed else 0}')")
            self.conn.commit()

        def get_words_len(self):
            self.cur.execute("SELECT COUNT(*) FROM stress")
            return self.cur.fetchall()[0][0]

        def get_word(self, id: int) -> Stress:
            self.cur.execute(f"SELECT * FROM stress WHERE id={id}")
            r = self.cur.fetchall()
            if len(r) == 0:
                return None
            return Stress(id, r[0][1], r[0][2])

        # periods:
        # 0 - all time
        # 1 - month
        # 2 - today

        def get_word_guess_logs_by_period(self, user_id, period) -> list:
            self.cur.execute(f"SELECT * FROM stress_guess_logs WHERE user_id={user_id} AND include_in_stats=1")
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
            return res[:max_words]  # (value, mistakes)

        def reset_stats(self, user_id):
            self.cur.execute(f"UPDATE stress_guess_logs SET include_in_stats=0 WHERE user_id={user_id}")
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
            return len(logs) == db.stress.get_words_goal(user_id)

        def problem_counter(self, user_id):
            self.cur.execute(f"UPDATE users SET problem_cnt=problem_cnt + 1 WHERE id={user_id}")
            self.conn.commit()

        def check_problem_cnt(self, user_id):
            self.cur.execute(f"SELECT problem_cnt FROM users WHERE id={user_id}")
            r = self.cur.fetchall()[0][0]
            if r >= RANDOM_INTERVAL:
                self.cur.execute(f"UPDATE users SET problem_cnt=0 WHERE id={user_id}")
                self.conn.commit()
                return True
            return False

        def add_to_problem_words(self, user_id, word_id):
            try:
                self.cur.execute(f"INSERT INTO problem_stress (user_id, word_id) VALUES ({user_id}, {word_id})")
                self.conn.commit()
            except Exception:
                pass

        def get_problem_word_ids(self, user_id):
            self.cur.execute(f"SELECT word_id FROM problem_stress WHERE user_id={user_id}")
            return [r[0] for r in self.cur.fetchall()]

        def remove_problem_word(self, user_id, word_id):
            self.cur.execute(f"DELETE FROM problem_stress WHERE user_id={user_id} AND word_id={word_id}")
            self.conn.commit()


    class _Users:
        def __init__(self, conn):
            self.conn = conn
            self.cur = self.conn.cursor()

        def get_all_users(self) -> list:
            self.cur.execute(f"SELECT * FROM users")
            return self.cur.fetchall()

        def check_user_exists(self, tg_id) -> bool:
            self.cur.execute(f"SELECT * FROM users WHERE tg_id='{tg_id}'")
            return len(self.cur.fetchall()) > 0

        def reg_user(self, tg_id, username, first_name):
            self.cur.execute(
                f"INSERT INTO users (tg_id, username, first_name, create_datetime) VALUES ('{tg_id}', '{username}', '{first_name}', '{current_datetime()}')")
            self.conn.commit()

        def get_username_by_tg_id(self, id):
            self.cur.execute(f"SELECT username FROM users WHERE tg_id={id}")
            return self.cur.fetchall()[0][0]

        def set_referal(self, tg_id, ref_id):
            self.cur.execute(f"UPDATE users SET referal='{ref_id}' WHERE tg_id={tg_id}")
            self.conn.commit()

        def get_refs_count(self, user_id):
            self.cur.execute(f"SELECT COUNT(*) FROM users WHERE referal={user_id}")
            return self.cur.fetchall()[0][0]

        def get_by_tg(self, tg_id):
            self.cur.execute(f"SELECT id FROM users WHERE tg_id='{tg_id}'")
            return self.cur.fetchall()[0][0]

        def check_sub_ad(self, user_id):
            self.cur.execute(f"SELECT sub_ad FROM users WHERE id={user_id}")
            r = self.cur.fetchall()[0][0]
            if r >= SHOW_SUBSCR_AD:
                self.cur.execute(f"UPDATE users SET sub_ad=0 WHERE id={user_id}")
                self.conn.commit()
                return True
            return False

        def sub_ad_count(self, user_id):
            self.cur.execute(f"UPDATE users SET sub_ad = sub_ad + 1 WHERE id={user_id}")
            self.conn.commit()

        def set_sub_ad(self, user_id, value):
            self.cur.execute(f"UPDATE users SET sub_ad={value} WHERE id={user_id}")
            self.conn.commit()

        def add_sub(self, user_id, days: int):
            self.cur.execute(f"SELECT sub_end FROM users WHERE id={user_id}")
            start = datetime.now()
            res = self.cur.fetchall()[0][0]
            if res is not None:
                start = (datetime.strptime(res, DB_DATETIME_FORMAT))
            else:
                self.cur.execute(
                    f"UPDATE users SET sub_start='{datetime.now().strftime(DB_DATETIME_FORMAT)}' WHERE id={user_id}")
            end = start + timedelta(days=days)
            self.cur.execute(f"UPDATE users SET sub_end='{end.strftime(DB_DATETIME_FORMAT)}' WHERE id={user_id}")
            self.conn.commit()

        def add_money(self, user_id, sum):
            self.cur.execute(f"UPDATE users SET balance=balance + {sum} WHERE id={user_id}")
            self.conn.commit()

        def remove_money(self, user_id, sum):
            self.cur.execute(f"UPDATE users SET balance=balance - {sum} WHERE id={user_id}")
            self.conn.commit()

        def get_balance(self, user_id):
            self.cur.execute(f"SELECT balance FROM users WHERE id={user_id}")
            return self.cur.fetchall()[0][0]

        def get_sub_end(self, user_id):
            self.cur.execute(f"SELECT sub_end FROM users WHERE id={user_id}")
            return self.cur.fetchall()[0][0]

        def check_sub(self, user_id) -> bool:
            current = datetime.now()
            end = self.get_sub_end(user_id)
            if end is None:
                return False
            end = datetime.strptime(self.get_sub_end(user_id), DB_DATETIME_FORMAT)
            return end > current

    class _Words:
        def __init__(self, conn):
            self.conn = conn
            self.cur = self.conn.cursor()

        def get_words_len(self):
            self.cur.execute("SELECT COUNT(*) FROM words")
            return self.cur.fetchall()[0][0]

        def get_word(self, id: int) -> Word:
            self.cur.execute(f"SELECT * FROM words WHERE id={id}")
            r = self.cur.fetchall()
            if len(r) == 0:
                return None
            return Word(r[0][0], r[0][1], r[0][2], r[0][3], r[0][4])

        def write_words(self, words: list):
            self.cur.execute(f"DELETE FROM words")
            for word in words:
                word, correct, comment, explain = word.value, word.solution, word.comment, word.explain
                self.cur.execute(f"INSERT INTO words (word, correct, comment, explain) VALUES ('{word}', '{correct}', '{comment}', '{explain}')")
            self.conn.commit()

db = DB('/Users/philippschepnov/PycharmProjects/rus_ege_stress_bot/database.db')
