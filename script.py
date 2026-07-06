import sqlite3

DB = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

for row in con.execute("""
SELECT
    id,
    start_date,
    end_date
FROM finance_balance_cycles
ORDER BY start_date;
"""):
    print(dict(row))

con.close()