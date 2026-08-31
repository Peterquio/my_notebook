import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)

IDS_REMOVER = (
    3363,  # Oxxo Fisher 18,69 - versão antiga 24/08
    3137,  # Mercado Livre 42,15 - versão antiga 19/08
    3136,  # Oxxo 15,80 - versão antiga 19/08
)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        print("=" * 90)
        print("LIMPEZA CIRÚRGICA - FATURA 09/2026")
        print("=" * 90)

        conn.execute("BEGIN")

        for expense_id in IDS_REMOVER:

            row = conn.execute(
                """
                SELECT
                    id,
                    effective_description,
                    effective_purchase_date,
                    effective_amount_cents,
                    installment_group_id,
                    status
                FROM finance_credit_card_expenses
                WHERE id = ?
                """,
                (expense_id,),
            ).fetchone()

            if row is None:
                print()
                print(
                    f"ID {expense_id}: já não existe."
                )
                continue

            print()
            print(
                f"DELETE ID {row['id']} | "
                f"{row['effective_purchase_date']} | "
                f"R$ {row['effective_amount_cents'] / 100:.2f} | "
                f"{row['effective_description']}"
            )

            conn.execute(
                """
                DELETE
                FROM finance_credit_card_expenses
                WHERE id = ?
                """,
                (expense_id,),
            )

        conn.commit()

        print()
        print("=" * 90)
        print("LIMPEZA CONCLUÍDA")
        print("=" * 90)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()