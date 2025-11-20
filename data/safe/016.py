
import sqlite3
cur = sqlite3.connect(':memory:').cursor()
cur.execute("SELECT * FROM users WHERE id = ?", (1,))
