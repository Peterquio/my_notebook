import sqlite3


import csv
import sqlite3
from collections import Counter

CAMINHO_DB = r"C:\dev\Outros\my_notebook\user_data\users\default.db"
CAMINHO_CSV = r"C:\dev\Outros\my_notebook\Nubank_2026-06-10.csv"
CREDIT_CARD_ID = 1
INVOICE_YEAR = 2026
INVOICE_MONTH = 5


def cents(valor: str) -> int:
    return int(round(float(valor.replace(",", ".")) * 100))


def assinatura(desc, data, valor):
    return (
        desc.strip().lower(),
        data,
        valor,
    )


csv_counter = Counter()

with open(CAMINHO_CSV, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        valor = cents(row["amount"])

        if valor <= 0:
            continue

        csv_counter[
            assinatura(row["title"], row["date"], valor)
        ] += 1


conexao = sqlite3.connect(CAMINHO_DB)
conexao.row_factory = sqlite3.Row

rows = conexao.execute("""
SELECT
    e.effective_description,
    e.effective_purchase_date,
    e.effective_amount_cents
FROM finance_credit_card_expenses e
INNER JOIN finance_credit_card_invoices i
    ON i.id = e.invoice_id
WHERE e.credit_card_id = ?
  AND i.invoice_year = ?
  AND i.invoice_month = ?
  AND e.status != 'cancelled'
ORDER BY e.effective_purchase_date, e.effective_description;
""", (CREDIT_CARD_ID, INVOICE_YEAR, INVOICE_MONTH)).fetchall()

db_counter = Counter()

for row in rows:
    db_counter[
        assinatura(
            row["effective_description"],
            row["effective_purchase_date"],
            row["effective_amount_cents"],
        )
    ] += 1

conexao.close()

print("\n=== NO DB MAS NÃO NO CSV ===")
for sig, qtd_db in db_counter.items():
    qtd_csv = csv_counter.get(sig, 0)

    if qtd_db > qtd_csv:
        desc, data, valor = sig
        print(f"{data} | {desc} | R$ {valor / 100:.2f} | DB={qtd_db} CSV={qtd_csv}")

print("\n=== NO CSV MAS NÃO NO DB ===")
for sig, qtd_csv in csv_counter.items():
    qtd_db = db_counter.get(sig, 0)

    if qtd_csv > qtd_db:
        desc, data, valor = sig
        print(f"{data} | {desc} | R$ {valor / 100:.2f} | CSV={qtd_csv} DB={qtd_db}")

print("\n=== TOTAIS ===")
print(f"CSV positivos: R$ {sum(valor * qtd for (_, _, valor), qtd in csv_counter.items()) / 100:.2f}")
print(f"DB positivos:  R$ {sum(valor * qtd for (_, _, valor), qtd in db_counter.items()) / 100:.2f}")