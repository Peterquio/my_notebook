import sqlite3

db_path = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

for table in [
    "finance_balance_income_entries",
    "finance_balance_commitments",
]:
    print("\n", table)
    cur.execute(f"PRAGMA table_info({table})")
    for row in cur.fetchall():
        if row[1] == "cycle_id":
            print(row)

conn.close()