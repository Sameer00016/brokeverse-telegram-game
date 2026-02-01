import sqlite3

conn = sqlite3.connect("game.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    taps INTEGER DEFAULT 1,
    claim_level INTEGER DEFAULT 1,
    referral_id INTEGER,
    paid INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    user_id INTEGER,
    item TEXT,
    amount REAL,
    tx_id TEXT
)
""")

conn.commit()
