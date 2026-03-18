import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "PeaceBreak.db")

def connect_db():
    os.makedirs(DATA_DIR, exist_ok=True)  # create data folder if needed
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_best_scores (
        player_id INTEGER PRIMARY KEY,
        best_score INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    """)

    conn.commit()
    conn.close()

    def add_player(username):
        conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO players (username)
    VALUES (?)
    """, (username,))

    conn.commit()
    conn.close()


def get_player_id(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT player_id FROM players
    WHERE username = ?
    """, (username,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None


def update_best_score(username, new_score):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO players (username) VALUES (?)", (username,))
    cursor.execute("SELECT player_id FROM players WHERE username = ?", (username,))
    player_id = cursor.fetchone()[0]

    cursor.execute("""
    INSERT INTO player_best_scores (player_id, best_score)
    VALUES (?, ?)
    ON CONFLICT(player_id) DO UPDATE SET best_score =
    CASE
        WHEN excluded.best_score > player_best_scores.best_score
        THEN excluded.best_score
        ELSE player_best_scores.best_score
    END
    """, (player_id, new_score))

    conn.commit()
    conn.close()


def get_leaderboard(limit=10):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT players.username, player_best_scores.best_score
    FROM player_best_scores
    JOIN players ON players.player_id = player_best_scores.player_id
    ORDER BY player_best_scores.best_score DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows