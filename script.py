import sqlite3

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
DELETE FROM finance_balance_commitments
WHERE commitment_origin = 'subscription_charge'
""")

conn.commit()
conn.close()

print("Compromissos removidos.")