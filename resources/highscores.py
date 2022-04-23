from datetime import datetime
import sqlite3

class Highscores:
    def check_schema():
        with sqlite3.connect("highscores.db") as db:
            db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER, name TEXT, created REAL, PRIMARY KEY (user_id) ON CONFLICT REPLACE)")
            db.execute("CREATE TABLE IF NOT EXISTS scoreboard (user_id INTEGER, score INTEGER, kills INTEGER, created REAL, PRIMARY KEY (user_id, created) ON CONFLICT REPLACE)")
            db.commit()
        
    def insert_user(name):
        created = datetime.timestamp(datetime.utcnow())
        with sqlite3.connect("highscores.db") as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (name, created) VALUES (?, ?)", (name, created))
            db.commit()
            return cursor.lastrowid

    def insert_score(user_id, score, kills):
        created = datetime.timestamp(datetime.utcnow())
        with sqlite3.connect("highscores.db") as db:
            db.execute("INSERT INTO scoreboard (user_id, score, kills, created) VALUES (?, ?, ?, ?)", (user_id, score, kills, created))
            db.commit()

    def select_all_scores(order_by="scoreboard.score"):
        # order_by is either string: user_id, score, kills, created
        with sqlite3.connect("highscores.db") as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT users.name, scoreboard.score, scoreboard.kills FROM users, scoreboard WHERE scoreboard.user_id = users.user_id ORDER BY {order_by} DESC")
            return cursor.fetchall()

    def select_score(user_id):
        with sqlite3.connect("highscores.db") as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT * FROM scoreboard WHERE user_id = ?", (user_id,))
            return cursor.fetchall()
        
    def select_names():
        with sqlite3.connect("highscores.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT user_id, name FROM users")
            return cursor.fetchall()

    def update_score(user_id, score, kills):
        with sqlite3.connect("highscores.db") as db:
            db.execute("UPDATE scoreboard SET score = ?, kills = ? WHERE user_id = ?", (score, kills, user_id))
            db.commit()

