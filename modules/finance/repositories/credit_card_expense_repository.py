from core.database.database_manager import DatabaseManager


class CreditCardExpenseRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_lancamento(
            self,
            credit_card_id: int,
            invoice_id: int,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            billing_date: str,
            installment_number: int,
            installment_total: int,
            effective_amount_cents: int,
            installment_group_id: str | None = None,
            notes: str | None = None,
            original_description: str | None = None,
            original_purchase_date: str | None = None,
            original_amount_cents: int | None = None,
            source_type: str | None = None,
            source_reference: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_card_expenses (
                credit_card_id,
                invoice_id,
                category_id,

                original_description,
                effective_description,

                original_purchase_date,
                effective_purchase_date,

                original_amount_cents,
                effective_amount_cents,

                billing_date,

                installment_number,
                installment_total,

                installment_group_id,

                source_type,
                source_reference,

                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                credit_card_id,
                invoice_id,
                category_id,

                original_description,
                effective_description,

                original_purchase_date,
                effective_purchase_date,

                original_amount_cents,
                effective_amount_cents,

                billing_date,

                installment_number,
                installment_total,

                installment_group_id,

                source_type,
                source_reference,

                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def somar_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(e.effective_amount_cents), 0) AS total_cents
            FROM finance_credit_card_expenses e
                     INNER JOIN finance_credit_card_invoices i
                                ON i.id = e.invoice_id
            WHERE e.credit_card_id = ?
              AND i.invoice_year = ?
              AND i.invoice_month = ?
              AND e.status != 'cancelled'
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
            ),
        )

        row = cursor.fetchone()

        return int(row["total_cents"])

    def listar_lancamentos_por_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.id,
                e.credit_card_id,
                e.invoice_id,
                e.category_id,

                e.effective_description,
                e.effective_purchase_date,
                e.effective_amount_cents,

                e.original_description,
                e.original_purchase_date,
                e.original_amount_cents,

                e.billing_date,
                e.installment_number,
                e.installment_total,
                e.installment_group_id,
                e.source_type,
                e.source_reference,
                e.status,

                c.name AS category_name,
                c.color AS category_color,

                i.invoice_year,
                i.invoice_month
            FROM finance_credit_card_expenses e
            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id
            LEFT JOIN finance_categories c
                ON c.id = e.category_id
            WHERE e.credit_card_id = ?
              AND i.invoice_year = ?
              AND i.invoice_month = ?
              AND e.status != 'cancelled'
            ORDER BY
                c.name,
                e.effective_purchase_date,
                e.effective_description,
                e.installment_number
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

    def listar_por_cartao(
            self,
            credit_card_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
            ORDER BY purchase_date
            """,
            (credit_card_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def atualizar_invoice_id(
            self,
            expense_id: int,
            invoice_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET invoice_id = ?
            WHERE id = ?
            """,
            (
                invoice_id,
                expense_id,
            ),
        )

        self.conexao.commit()