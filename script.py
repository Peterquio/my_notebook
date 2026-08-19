import sqlite3
import shutil
from pathlib import Path
from datetime import datetime


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)

CREDIT_CARD_ID = 1
INVOICE_YEAR = 2026
INVOICE_MONTH = 9


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado:\n{DB_PATH}"
        )

    # ---------------------------------------------------------
    # BACKUP
    # ---------------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = DB_PATH.with_name(
        f"{DB_PATH.stem}_backup_limpeza_setembro_{timestamp}.db"
    )

    shutil.copy2(
        DB_PATH,
        backup_path,
    )

    print("=" * 70)
    print("LIMPEZA DA FATURA 09/2026")
    print("=" * 70)
    print()
    print(f"Banco : {DB_PATH}")
    print(f"Backup: {backup_path}")
    print()

    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row

    try:
        cursor = conexao.cursor()

        # -----------------------------------------------------
        # LOCALIZA FATURA
        # -----------------------------------------------------
        cursor.execute(
            """
            SELECT id
            FROM finance_credit_card_invoices
            WHERE credit_card_id = ?
              AND invoice_year = ?
              AND invoice_month = ?
            """,
            (
                CREDIT_CARD_ID,
                INVOICE_YEAR,
                INVOICE_MONTH,
            ),
        )

        invoice = cursor.fetchone()

        if invoice is None:
            raise ValueError(
                "Fatura 09/2026 não encontrada."
            )

        invoice_id = int(invoice["id"])

        print(f"Fatura encontrada: ID {invoice_id}")
        print()

        # -----------------------------------------------------
        # LOCALIZA IMPORTAÇÕES CSV DE SETEMBRO
        # -----------------------------------------------------
        cursor.execute(
            """
            SELECT
                id,
                import_batch_id,
                installment_group_id,
                effective_description,
                installment_number,
                installment_total
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND invoice_id = ?
              AND created_by = 'csv_import'
            """,
            (
                CREDIT_CARD_ID,
                invoice_id,
            ),
        )

        importados = [
            dict(row)
            for row in cursor.fetchall()
        ]

        if not importados:
            print(
                "Nenhum lançamento CSV encontrado "
                "na fatura de setembro."
            )
            return

        batch_ids = {
            row["import_batch_id"]
            for row in importados
            if row["import_batch_id"] is not None
        }

        grupos_importados = {
            row["installment_group_id"]
            for row in importados
            if row["installment_group_id"]
        }

        print(
            f"Lançamentos CSV encontrados: "
            f"{len(importados)}"
        )

        print(
            f"Lotes encontrados: "
            f"{sorted(batch_ids)}"
        )

        print(
            f"Grupos parcelados envolvidos: "
            f"{len(grupos_importados)}"
        )

        # -----------------------------------------------------
        # MOSTRA MANUAIS QUE SERÃO PRESERVADOS
        # -----------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND invoice_id = ?
              AND (
                    created_by IS NULL
                    OR created_by != 'csv_import'
                  )
              AND status != 'cancelled'
            """,
            (
                CREDIT_CARD_ID,
                invoice_id,
            ),
        )

        total_preservados = int(
            cursor.fetchone()["total"]
        )

        print(
            f"Lançamentos não importados preservados: "
            f"{total_preservados}"
        )

        # -----------------------------------------------------
        # CONTA PROJEÇÕES CONTAMINADAS
        # -----------------------------------------------------
        total_projecoes = 0

        if grupos_importados:
            placeholders = ",".join(
                "?"
                for _ in grupos_importados
            )

            cursor.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM finance_credit_card_expenses
                WHERE credit_card_id = ?
                  AND source_type = 'projected_installment'
                  AND installment_group_id IN ({placeholders})
                """,
                (
                    CREDIT_CARD_ID,
                    *grupos_importados,
                ),
            )

            total_projecoes = int(
                cursor.fetchone()["total"]
            )

        print(
            f"Projeções ligadas a esses grupos: "
            f"{total_projecoes}"
        )

        print()
        print("-" * 70)
        print("EXECUTANDO LIMPEZA")
        print("-" * 70)

        conexao.execute("BEGIN")

        # -----------------------------------------------------
        # 1. APAGA TODAS AS PROJEÇÕES DOS GRUPOS TOCADOS
        #
        # Inclui projeções antigas, futuras, ativas ou canceladas.
        # Não toca em parcelas reais.
        # -----------------------------------------------------
        if grupos_importados:
            placeholders = ",".join(
                "?"
                for _ in grupos_importados
            )

            cursor.execute(
                f"""
                DELETE FROM finance_credit_card_expenses
                WHERE credit_card_id = ?
                  AND source_type = 'projected_installment'
                  AND installment_group_id IN ({placeholders})
                """,
                (
                    CREDIT_CARD_ID,
                    *grupos_importados,
                ),
            )

            print(
                f"Projeções removidas: "
                f"{cursor.rowcount}"
            )

        # -----------------------------------------------------
        # 2. APAGA OS LANÇAMENTOS CSV DA FATURA DE SETEMBRO
        # -----------------------------------------------------
        cursor.execute(
            """
            DELETE FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND invoice_id = ?
              AND created_by = 'csv_import'
            """,
            (
                CREDIT_CARD_ID,
                invoice_id,
            ),
        )

        print(
            f"Lançamentos CSV removidos: "
            f"{cursor.rowcount}"
        )

        # -----------------------------------------------------
        # 3. REMOVE OS LOTES QUE FICARAM SEM LANÇAMENTOS
        # -----------------------------------------------------
        lotes_removidos = 0

        for batch_id in batch_ids:
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM finance_credit_card_expenses
                WHERE import_batch_id = ?
                """,
                (batch_id,),
            )

            restante = int(
                cursor.fetchone()["total"]
            )

            if restante == 0:
                cursor.execute(
                    """
                    DELETE FROM finance_credit_card_import_batches
                    WHERE id = ?
                    """,
                    (batch_id,),
                )

                lotes_removidos += cursor.rowcount

        print(
            f"Lotes de importação removidos: "
            f"{lotes_removidos}"
        )

        conexao.commit()

        # -----------------------------------------------------
        # CONFERÊNCIA
        # -----------------------------------------------------
        print()
        print("-" * 70)
        print("CONFERÊNCIA")
        print("-" * 70)

        cursor.execute(
            """
            SELECT
                created_by,
                source_type,
                status,
                COUNT(*) AS total
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND invoice_id = ?
            GROUP BY
                created_by,
                source_type,
                status
            ORDER BY
                created_by,
                source_type,
                status
            """,
            (
                CREDIT_CARD_ID,
                invoice_id,
            ),
        )

        rows = cursor.fetchall()

        if not rows:
            print("Fatura ficou sem lançamentos.")
        else:
            for row in rows:
                print(
                    f"created_by={row['created_by']} | "
                    f"source_type={row['source_type']} | "
                    f"status={row['status']} | "
                    f"total={row['total']}"
                )

        print()
        print("=" * 70)
        print("LIMPEZA CONCLUÍDA")
        print("=" * 70)
        print()
        print(
            "Agora pode abrir o My Notebook "
            "e importar novamente a fatura de setembro."
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    main()