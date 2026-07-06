import sqlite3

DB = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

con = sqlite3.connect(DB)
cur = con.cursor()

cur.execute("""
DELETE FROM finance_balance_commitments
WHERE external_reference LIKE 'cc:%:payment:%';
""")

con.commit()

print(f"Compromissos de pagamento removidos: {cur.rowcount}")

con.close()