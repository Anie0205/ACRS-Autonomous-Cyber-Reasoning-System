
import sqlite3
db = sqlite3.connect(':memory:')
cur = db.cursor()
user = input()
query = "SELECT * FROM users WHERE id = " + user
cur.execute(query)
