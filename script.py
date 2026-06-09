import sqlite3

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"


def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return coluna in [linha[1] for linha in cursor.fetchall()]


with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()

    alteracoes = [
        (
            "finance_balance_commitments",
            "commitment_origin",
            "ALTER TABLE finance_balance_commitments "
            "ADD COLUMN commitment_origin TEXT NOT NULL DEFAULT 'manual'"
        ),
        (
            "finance_balance_commitments",
            "projection_type",
            "ALTER TABLE finance_balance_commitments "
            "ADD COLUMN projection_type TEXT NOT NULL DEFAULT 'real'"
        ),
        (
            "finance_credit_card_invoices",
            "closed_by",
            "ALTER TABLE finance_credit_card_invoices "
            "ADD COLUMN closed_by TEXT"
        ),
        (
            "finance_credit_card_invoices",
            "closed_at",
            "ALTER TABLE finance_credit_card_invoices "
            "ADD COLUMN closed_at TEXT"
        ),
    ]

    for tabela, coluna, sql in alteracoes:
        if coluna_existe(cursor, tabela, coluna):
            print(f"OK: {tabela}.{coluna} já existe")
        else:
            cursor.execute(sql)
            print(f"CRIADO: {tabela}.{coluna}")

    conn.commit()

print("Migração concluída.")