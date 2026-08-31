import csv
import sqlite3
from collections import Counter
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)

CSV_PATH = Path(
    r"C:\dev\Outros\my_notebook\Nubank_2026-09-10.csv"
)


def parse_amount(value: str) -> int:
    value = value.strip()
    value = value.replace("R$", "")
    value = value.replace(" ", "")
    value = value.replace(".", "")
    value = value.replace(",", ".")

    return round(float(value) * 100)


def main():
    print("=" * 100)
    print("AUDITORIA DE MULTIPLICIDADE DOS AJUSTES")
    print("=" * 100)

    csv_counter = Counter()

    with CSV_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            amount = parse_amount(row["amount"])

            if amount >= 0:
                continue

            key = (
                row["date"].strip(),
                row["title"].strip(),
                amount,
            )

            csv_counter[key] += 1

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            adjustment_date,
            source_reference,
            amount_cents,
            COUNT(*) AS quantidade
        FROM finance_credit_card_invoice_adjustments
        WHERE status != 'cancelled'
        GROUP BY
            adjustment_date,
            source_reference,
            amount_cents
        """
    ).fetchall()

    db_counter = {
        (
            row["adjustment_date"],
            row["source_reference"],
            row["amount_cents"],
        ): row["quantidade"]
        for row in rows
    }

    conn.close()

    for key, csv_count in sorted(
        csv_counter.items()
    ):
        db_count = db_counter.get(key, 0)

        data, titulo, amount = key

        status = "OK"

        if db_count < csv_count:
            status = "FALTANDO"

        elif db_count > csv_count:
            status = "EXCEDENTE"

        print()
        print(f"{status}")
        print(f"Data       : {data}")
        print(f"Descrição  : {titulo}")
        print(f"Valor      : R$ {amount / 100:.2f}")
        print(f"CSV        : {csv_count}")
        print(f"Banco      : {db_count}")
        print(f"Diferença  : {db_count - csv_count:+d}")


if __name__ == "__main__":
    main()