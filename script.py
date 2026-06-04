import sqlite3

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conexao = sqlite3.connect(DB_PATH)
conexao.row_factory = sqlite3.Row
cursor = conexao.cursor()

cursor.execute("""
    SELECT
        id,
        cycle_id,
        description,
        expected_amount_cents,
        due_date,
        status,
        is_recurring,
        external_reference
    FROM finance_balance_commitments
    WHERE external_reference LIKE 'template:%'
    ORDER BY id ASC
""")

for row in cursor.fetchall():
    print(dict(row))

conexao.close()