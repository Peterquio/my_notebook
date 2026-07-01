import sqlite3

db_path = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Descobre o id do Nubank
cur.execute("""
SELECT id, name
FROM finance_credit_cards
WHERE name LIKE '%Nubank%'
""")

row = cur.fetchone()

if row is None:
    print("Cartão Nubank não encontrado.")
    conn.close()
    raise SystemExit

credit_card_id = row[0]

print(f"Limpando cartão: {row[1]} (id={credit_card_id})")

# Ajustes
cur.execute("""
DELETE FROM finance_credit_card_invoice_adjustments
WHERE credit_card_id = ?
""", (credit_card_id,))

# Lançamentos
cur.execute("""
DELETE FROM finance_credit_card_expenses
WHERE credit_card_id = ?
""", (credit_card_id,))

# Lotes de importação
cur.execute("""
DELETE FROM finance_credit_card_import_batches
WHERE credit_card_id = ?
""", (credit_card_id,))

# Faturas
cur.execute("""
DELETE FROM finance_credit_card_invoices
WHERE credit_card_id = ?
""", (credit_card_id,))

conn.commit()
conn.close()

print("Cartão limpo com sucesso.")