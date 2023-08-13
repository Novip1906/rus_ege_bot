import sqlite3


class DB:
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cur = self.conn.cursor()
            print("База данных подключена")

        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)

    def get_adm_lvl(self, tg_id) -> int:
        self.cur.execute(f"SELECT admin_lvl FROM users WHERE tg_id=?", (tg_id,))
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0][0]
        return None


db = DB('../database.db')