import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def moeda(cents: int) -> str:
    return f"R$ {cents / 100:.2f}".replace(".", ",")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            e.id,
            e.effective_description,
            e.effective_purchase_date,
            e.effective_amount_cents,
            e.installment_number,
            e.installment_total,
            e.source_type,
            e.installment_group_id,
            e.status
        FROM finance_credit_card_expenses e
        INNER JOIN finance_credit_card_invoices i
            ON i.id = e.invoice_id
        WHERE i.invoice_year = 2026
          AND i.invoice_month = 9
          AND e.status != 'cancelled'
        ORDER BY
            e.effective_amount_cents DESC,
            e.id
        """
    )

    expenses = cursor.fetchall()

    total_expenses = sum(
        row["effective_amount_cents"]
        for row in expenses
    )

    print("=" * 100)
    print("FATURA SETEMBRO/2026 - LANÇAMENTOS ATIVOS")
    print("=" * 100)

    for row in expenses:
        parcela = "-"

        if row["installment_total"] > 1:
            parcela = (
                f"{row['installment_number']}/"
                f"{row['installment_total']}"
            )

        print(
            f"{row['id']:>5} | "
            f"{moeda(row['effective_amount_cents']):>10} | "
            f"{parcela:>6} | "
            f"{str(row['source_type']):<22} | "
            f"{row['effective_purchase_date']} | "
            f"{row['effective_description']}"
        )

    print()
    print(
        f"TOTAL LANÇAMENTOS: {moeda(total_expenses)}"
    )

    cursor.execute(
        """
        SELECT
            a.id,
            a.adjustment_type,
            a.description,
            a.adjustment_date,
            a.amount_cents,
            a.source_type
        FROM finance_credit_card_invoice_adjustments a
        INNER JOIN finance_credit_card_invoices i
            ON i.id = a.invoice_id
        WHERE i.invoice_year = 2026
          AND i.invoice_month = 9
        ORDER BY a.id
        """
    )

    adjustments = cursor.fetchall()

    total_adjustments = sum(
        row["amount_cents"]
        for row in adjustments
    )

    print()
    print("=" * 100)
    print("AJUSTES")
    print("=" * 100)

    for row in adjustments:
        print(
            f"{row['id']:>5} | "
            f"{moeda(row['amount_cents']):>10} | "
            f"{row['adjustment_type']:<28} | "
            f"{row['adjustment_date']} | "
            f"{row['description']}"
        )

    print()
    print(
        f"TOTAL AJUSTES: {moeda(total_adjustments)}"
    )

    total_final = (
        total_expenses
        + total_adjustments
    )

    print()
    print("=" * 100)
    print(f"TOTAL CALCULADO : {moeda(total_final)}")
    print(f"TOTAL NUBANK    : R$ 3.836,31")
    print(
        f"DIFERENÇA       : "
        f"{moeda(total_final - 383631)}"
    )
    print("=" * 100)

    conn.close()


if __name__ == "__main__":
    main()