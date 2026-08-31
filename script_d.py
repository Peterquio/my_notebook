import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


PARES = (
    # ID que permanece, ID mais novo que será absorvido
    (3364, 3552),
    (3365, 3554),
)


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado:\n{DB_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("BEGIN")

        for id_manter, id_novo in PARES:

            antigo = conn.execute(
                """
                SELECT *
                FROM finance_credit_card_expenses
                WHERE id = ?
                """,
                (id_manter,),
            ).fetchone()

            novo = conn.execute(
                """
                SELECT *
                FROM finance_credit_card_expenses
                WHERE id = ?
                """,
                (id_novo,),
            ).fetchone()

            if antigo is None:
                raise RuntimeError(
                    f"ID antigo não encontrado: {id_manter}"
                )

            if novo is None:
                raise RuntimeError(
                    f"ID novo não encontrado: {id_novo}"
                )

            if (
                antigo["installment_group_id"]
                != novo["installment_group_id"]
            ):
                raise RuntimeError(
                    f"Grupos diferentes: "
                    f"{id_manter} x {id_novo}"
                )

            if (
                antigo["installment_number"]
                != novo["installment_number"]
            ):
                raise RuntimeError(
                    f"Parcelas diferentes: "
                    f"{id_manter} x {id_novo}"
                )

            if (
                antigo["installment_total"]
                != novo["installment_total"]
            ):
                raise RuntimeError(
                    f"Totais diferentes: "
                    f"{id_manter} x {id_novo}"
                )

            if (
                antigo["original_description"]
                != novo["original_description"]
            ):
                raise RuntimeError(
                    f"Descrições diferentes: "
                    f"{id_manter} x {id_novo}"
                )

            if (
                antigo["original_amount_cents"]
                != novo["original_amount_cents"]
            ):
                raise RuntimeError(
                    f"Valores diferentes: "
                    f"{id_manter} x {id_novo}"
                )

            #
            # Preserva o lançamento original,
            # mas atualiza nele a realidade
            # trazida pela importação mais recente.
            #
            conn.execute(
                """
                UPDATE finance_credit_card_expenses
                SET
                    invoice_id = ?,

                    original_description = ?,
                    original_purchase_date = ?,
                    original_amount_cents = ?,

                    effective_purchase_date = ?,
                    effective_amount_cents = ?,

                    billing_date = ?,

                    source_type = ?,
                    source_reference = ?,
                    import_batch_id = ?,

                    updated_at = CURRENT_TIMESTAMP

                WHERE id = ?
                """,
                (
                    novo["invoice_id"],

                    novo["original_description"],
                    novo["original_purchase_date"],
                    novo["original_amount_cents"],

                    novo["effective_purchase_date"],
                    novo["effective_amount_cents"],

                    novo["billing_date"],

                    novo["source_type"],
                    novo["source_reference"],
                    novo["import_batch_id"],

                    id_manter,
                ),
            )

            #
            # A linha nova deixa de representar
            # uma compra ativa.
            #
            conn.execute(
                """
                UPDATE finance_credit_card_expenses
                SET
                    status = 'cancelled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (id_novo,),
            )

            print()
            print(
                f"{id_novo} absorvido por {id_manter}"
            )

            print(
                f"Grupo   : "
                f"{antigo['installment_group_id']}"
            )

            print(
                f"Parcela : "
                f"{antigo['installment_number']}/"
                f"{antigo['installment_total']}"
            )

            print(
                f"Data    : "
                f"{antigo['original_purchase_date']} "
                f"-> {novo['original_purchase_date']}"
            )

            print(
                f"Batch   : "
                f"{antigo['import_batch_id']} "
                f"-> {novo['import_batch_id']}"
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    print()
    print("=" * 80)
    print("NORMALIZAÇÃO CONCLUÍDA")
    print("=" * 80)


if __name__ == "__main__":
    main()