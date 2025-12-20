import sqlite3

conn = sqlite3.connect('charity_fund.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute('SELECT request_id, status, succeeded FROM grant_requests LIMIT 5').fetchall()

for r in rows:
    print(f'ID: {r["request_id"]}, status: {r["status"]}, succeeded: {r["succeeded"]}')

conn.close()
