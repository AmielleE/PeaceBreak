import sqlite3
import os
import sys

# Get database path
def get_db_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "PeaceBreak.db")

def connect_db():
    return sqlite3.connect(get_db_path())

# Create tables if they don't exist
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

# Player management functions
def add_player(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO players (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def get_player_id(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT player_id FROM players WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# Score management functions
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

def get_leaderboard_as_dicts(limit=10):
    rows = get_leaderboard(limit)
    return [{"name": row[0], "score": row[1]} for row in rows]