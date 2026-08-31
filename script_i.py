import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print("=" * 100)
    print("ÚLTIMOS LANÇAMENTOS")
    print("=" * 100)

    rows = conn.execute(
        """
        SELECT
            id,
            original_description,
            original_purchase_date,
            original_amount_cents,
            installment_number,
            installment_total,
            import_batch_id,
            status,
            created_at,
            updated_at
        FROM finance_credit_card_expenses
        ORDER BY id DESC
        LIMIT 20
        """
    ).fetchall()

    for row in rows:
        print(
            f"ID {row['id']:>5} | "
            f"{row['original_purchase_date']} | "
            f"R$ {row['original_amount_cents'] / 100:>8.2f} | "
            f"batch={row['import_batch_id']} | "
            f"{row['status']:<10} | "
            f"{row['original_description']}"
        )

    print()
    print("=" * 100)
    print("ÚLTIMOS AJUSTES")
    print("=" * 100)

    rows = conn.execute(
        """
        SELECT
            id,
            adjustment_type,
            description,
            adjustment_date,
            amount_cents,
            source_reference,
            status,
            created_at,
            updated_at
        FROM finance_credit_card_invoice_adjustments
        ORDER BY id DESC
        LIMIT 30
        """
    ).fetchall()

    for row in rows:
        print(
            f"ID {row['id']:>5} | "
            f"{row['adjustment_date']} | "
            f"R$ {row['amount_cents'] / 100:>8.2f} | "
            f"{row['status']:<10} | "
            f"{row['source_reference']}"
        )

    conn.close()


if __name__ == "__main__":
    main()