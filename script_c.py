import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)

IDS = (
    3364,
    3552,
    3365,
    3554,
)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    placeholders = ",".join(
        "?"
        for _ in IDS
    )

    cursor.execute(
        f"""
        SELECT
            e.id,
            e.installment_group_id,

            e.original_description,
            e.effective_description,

            e.original_purchase_date,
            e.effective_purchase_date,

            e.original_amount_cents,
            e.effective_amount_cents,

            e.installment_number,
            e.installment_total,

            e.source_type,
            e.source_reference,

            e.import_batch_id,
            e.created_by,

            e.status,
            e.created_at,
            e.updated_at,

            i.invoice_year,
            i.invoice_month

        FROM finance_credit_card_expenses e

        INNER JOIN finance_credit_card_invoices i
            ON i.id = e.invoice_id

        WHERE e.id IN ({placeholders})

        ORDER BY
            e.installment_group_id,
            e.id
        """,
        IDS,
    )

    rows = cursor.fetchall()

    print("=" * 100)
    print("AUDITORIA DOS 4 LANCAMENTOS REAIS")
    print("=" * 100)

    for row in rows:
        print()
        print("-" * 100)

        print(f"ID                     : {row['id']}")
        print(f"Grupo                  : {row['installment_group_id']}")

        print(
            f"Descrição original     : "
            f"{row['original_description']}"
        )

        print(
            f"Descrição efetiva      : "
            f"{row['effective_description']}"
        )

        print(
            f"Data original          : "
            f"{row['original_purchase_date']}"
        )

        print(
            f"Data efetiva           : "
            f"{row['effective_purchase_date']}"
        )

        print(
            f"Valor original         : "
            f"{row['original_amount_cents']}"
        )

        print(
            f"Valor efetivo          : "
            f"{row['effective_amount_cents']}"
        )

        print(
            f"Parcela                : "
            f"{row['installment_number']}/"
            f"{row['installment_total']}"
        )

        print(
            f"Fatura                 : "
            f"{row['invoice_month']:02d}/"
            f"{row['invoice_year']}"
        )

        print(
            f"Source type            : "
            f"{row['source_type']}"
        )

        print(
            f"Source reference       : "
            f"{row['source_reference']}"
        )

        print(
            f"Import batch           : "
            f"{row['import_batch_id']}"
        )

        print(
            f"Created by             : "
            f"{row['created_by']}"
        )

        print(
            f"Status                 : "
            f"{row['status']}"
        )

        print(
            f"Created at             : "
            f"{row['created_at']}"
        )

        print(
            f"Updated at             : "
            f"{row['updated_at']}"
        )

    conn.close()


if __name__ == "__main__":
    main()