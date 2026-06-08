import csv
import sqlite3
from decimal import Decimal

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"
CSV_PATH = r"C:\dev\Outros\my_notebook\user_data\users\Nubank_2026-03-10.csv"

DATA_INICIO = "2026-02-03"
DATA_FIM = "2026-03-02"

def centavos(valor):
    texto = str(valor).replace("R$", "").replace(",", ".").strip()
    return int((Decimal(texto) * 100).quantize(Decimal("1")))

total_csv = 0

with open(CSV_PATH, "r", encoding="utf-8-sig") as arquivo:
    leitor = csv.DictReader(arquivo)

    print("COLUNAS CSV:", leitor.fieldnames)

    for linha in leitor:
        texto_linha = " | ".join(str(v) for v in linha.values())

        # ajuste se o nome da coluna de data/valor for diferente
        data = linha.get("date") or linha.get("Data") or linha.get("data")
        valor = linha.get("amount") or linha.get("Valor") or linha.get("valor")

        if not data or not valor:
            continue

        if DATA_INICIO <= data <= DATA_FIM:
            valor_centavos = centavos(valor)

            if valor_centavos > 0:
                total_csv += valor_centavos

print(f"TOTAL CSV POSITIVO: R$ {total_csv / 100:.2f}")

con = sqlite3.connect(DB_PATH)
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute(
    """
    SELECT SUM(effective_amount_cents) AS total
    FROM finance_credit_card_expenses
    WHERE effective_purchase_date >= ?
      AND effective_purchase_date <= ?
      AND status != 'cancelled'
      AND created_by = 'csv_import'
    """,
    (DATA_INICIO, DATA_FIM),
)

total_db = cur.fetchone()["total"] or 0

print(f"TOTAL DB POSITIVO:  R$ {total_db / 100:.2f}")
print(f"DIFERENÇA:          R$ {(total_db - total_csv) / 100:.2f}")

con.close()