from core.database.database_manager import DatabaseManager


class CreditCardInvoiceAdjustmentRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_ajuste(
            self,
            credit_card_id: int,
            invoice_id: int,
            adjustment_type: str,
            description: str,
            adjustment_date: str,
            amount_cents: int,
            source_type: str | None = None,
            source_reference: str | None = None,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_card_invoice_adjustments (
                credit_card_id,
                invoice_id,
                adjustment_type,
                description,
                adjustment_date,
                amount_cents,
                source_type,
                source_reference,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                credit_card_id,
                invoice_id,
                adjustment_type,
                description,
                adjustment_date,
                amount_cents,
                source_type,
                source_reference,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def somar_ajustes_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(a.amount_cents), 0) AS total_cents
            FROM finance_credit_card_invoice_adjustments a
            INNER JOIN finance_credit_card_invoices i
                ON i.id = a.invoice_id
            WHERE a.credit_card_id = ?
              AND i.invoice_year = ?
              AND i.invoice_month = ?
              AND a.status != 'cancelled'
              AND a.adjustment_type != 'previous_invoice_payment'
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
            ),
        )

        row = cursor.fetchone()

        return int(row["total_cents"] or 0)

    def listar_ajustes_importados_fatura(
            self,
            credit_card_id: int,
            invoice_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_invoice_adjustments
            WHERE credit_card_id = ?
              AND invoice_id = ?
              AND status != 'cancelled'
              AND notes LIKE 'Ajuste importado via CSV%'
            ORDER BY id ASC
            """,
            (
                credit_card_id,
                invoice_id,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def cancelar_ajuste_importado(
            self,
            adjustment_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_invoice_adjustments
            SET
                status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status != 'cancelled'
            """,
            (adjustment_id,),
        )

        self.conexao.commit()

    def listar_ajustes_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                a.id,
                a.credit_card_id,
                a.invoice_id,
                a.adjustment_type,
                a.description,
                a.adjustment_date,
                a.amount_cents,
                a.source_type,
                a.source_reference,
                a.notes,
                a.status,
                a.created_at,
                a.updated_at
            FROM finance_credit_card_invoice_adjustments a
            INNER JOIN finance_credit_card_invoices i
                ON i.id = a.invoice_id
            WHERE a.credit_card_id = ?
              AND i.invoice_year = ?
              AND i.invoice_month = ?
              AND a.status != 'cancelled'
              AND a.adjustment_type != 'previous_invoice_payment'
            ORDER BY a.adjustment_date ASC, a.id ASC
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]