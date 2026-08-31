import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def moeda(cents):
    if cents is None:
        return "-"

    return f"R$ {cents / 100:.2f}"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print("=" * 120)
    print("AUDITORIA DOS LANÇAMENTOS NOVOS")
    print("=" * 120)

    rows = conn.execute(
        """
        SELECT
            e.id,

            e.original_description,
            e.effective_description,

            e.original_purchase_date,
            e.effective_purchase_date,

            e.original_amount_cents,
            e.effective_amount_cents,

            e.installment_number,
            e.installment_total,
            e.installment_group_id,

            e.source_type,
            e.source_reference,

            e.import_batch_id,
            e.created_by,

            e.status,
            e.notes,

            e.created_at,
            e.updated_at,

            i.invoice_year,
            i.invoice_month

        FROM finance_credit_card_expenses e

        LEFT JOIN finance_credit_card_invoices i
            ON i.id = e.invoice_id

        WHERE e.id >= 3555

        ORDER BY e.id
        """
    ).fetchall()

    for row in rows:

        print()
        print("-" * 120)

        print(f"ID              : {row['id']}")

        print(
            f"Fatura          : "
            f"{row['invoice_month']:02d}/"
            f"{row['invoice_year']}"
        )

        print(
            f"Descrição       : "
            f"{row['effective_description']}"
        )

        print(
            f"Original        : "
            f"{row['original_description']}"
        )

        print(
            f"Data original   : "
            f"{row['original_purchase_date']}"
        )

        print(
            f"Data efetiva    : "
            f"{row['effective_purchase_date']}"
        )

        print(
            f"Valor original  : "
            f"{moeda(row['original_amount_cents'])}"
        )

        print(
            f"Valor efetivo   : "
            f"{moeda(row['effective_amount_cents'])}"
        )

        print(
            f"Parcela         : "
            f"{row['installment_number']}/"
            f"{row['installment_total']}"
        )

        print(
            f"Grupo           : "
            f"{row['installment_group_id']}"
        )

        print(
            f"Source type     : "
            f"{row['source_type']}"
        )

        print(
            f"Source reference: "
            f"{row['source_reference']}"
        )

        print(
            f"Import batch    : "
            f"{row['import_batch_id']}"
        )

        print(
            f"Created by      : "
            f"{row['created_by']}"
        )

        print(
            f"Status          : "
            f"{row['status']}"
        )

        print(
            f"Notes           : "
            f"{row['notes']}"
        )

        print(
            f"Created at      : "
            f"{row['created_at']}"
        )

        print(
            f"Updated at      : "
            f"{row['updated_at']}"
        )

    print()
    print()
    print("=" * 120)
    print("RESUMO POR SOURCE TYPE / CREATED BY")
    print("=" * 120)

    resumo = conn.execute(
        """
        SELECT
            source_type,
            created_by,
            status,
            COUNT(*) AS quantidade,
            MIN(id) AS primeiro_id,
            MAX(id) AS ultimo_id

        FROM finance_credit_card_expenses

        WHERE id >= 3555

        GROUP BY
            source_type,
            created_by,
            status

        ORDER BY quantidade DESC
        """
    ).fetchall()

    for row in resumo:
        print(
            f"{row['quantidade']:>5} | "
            f"IDs {row['primeiro_id']} -> {row['ultimo_id']} | "
            f"status={row['status']} | "
            f"source={row['source_type']} | "
            f"created_by={row['created_by']}"
        )

    print()
    print()
    print("=" * 120)
    print("GRUPOS COM MAIS DE UMA PARCELA ATIVA DO MESMO NÚMERO")
    print("=" * 120)

    duplicados = conn.execute(
        """
        SELECT
            installment_group_id,
            installment_number,
            COUNT(*) AS quantidade,
            GROUP_CONCAT(id) AS ids,
            GROUP_CONCAT(source_type) AS source_types

        FROM finance_credit_card_expenses

        WHERE id >= 3555
          AND status != 'cancelled'
          AND installment_group_id IS NOT NULL

        GROUP BY
            installment_group_id,
            installment_number

        HAVING COUNT(*) > 1

        ORDER BY quantidade DESC
        """
    ).fetchall()

    if not duplicados:
        print("Nenhum.")

    else:
        for row in duplicados:
            print()
            print(
                f"Grupo   : "
                f"{row['installment_group_id']}"
            )

            print(
                f"Parcela : "
                f"{row['installment_number']}"
            )

            print(
                f"Quantidade: "
                f"{row['quantidade']}"
            )

            print(
                f"IDs      : "
                f"{row['ids']}"
            )

            print(
                f"Sources  : "
                f"{row['source_types']}"
            )

    conn.close()


if __name__ == "__main__":
    main()