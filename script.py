import sqlite3

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(finance_balance_commitments)")
cols = {row[1] for row in cursor.fetchall()}

columns_to_add = {
    "status": "TEXT NOT NULL DEFAULT 'expected'",
    "external_reference": "TEXT",
}

for col, definition in columns_to_add.items():
    if col not in cols:
        cursor.execute(
            f"ALTER TABLE finance_balance_commitments ADD COLUMN {col} {definition}"
        )
        print(f"[ADD] {col}")
    else:
        print(f"[OK] {col}")

conn.commit()
conn.close()

print("Migração concluída.")