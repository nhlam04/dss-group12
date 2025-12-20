import sqlite3

conn = sqlite3.connect('charity_fund.db')
cursor = conn.cursor()

cursor.execute('SELECT request_id, program_name, status, succeeded FROM grant_requests LIMIT 10')
print("Current grant requests:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Program: {row[1][:30]}, Status: {row[2]}, Succeeded: {row[3]}")

cursor.execute('SELECT DISTINCT status FROM grant_requests')
print("\nDistinct statuses:")
for row in cursor.fetchall():
    print(f"  {row[0]}")

conn.close()
