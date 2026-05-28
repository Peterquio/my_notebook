import sqlite3

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
SELECT
    e.id,
    i.invoice_year,
    i.invoice_month,
    e.effective_description,
    e.effective_purchase_date,
    e.installment_number,
    e.installment_total,
    e.effective_amount_cents,
    e.source_type,
    e.source_reference,
    e.installment_group_id,
    e.status
FROM finance_credit_card_expenses e
INNER JOIN finance_credit_card_invoices i
    ON i.id = e.invoice_id
WHERE e.effective_description LIKE '%Cea Wps%'
ORDER BY
    e.effective_amount_cents,
    e.installment_total,
    e.installment_number,
    i.invoice_year,
    i.invoice_month,
    e.id
""")

for row in cursor.fetchall():
    print(dict(row))

conn.close()