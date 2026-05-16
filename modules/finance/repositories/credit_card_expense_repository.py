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
            description: str,
            purchase_date: str,
            billing_date: str,
            installment_number: int,
            installment_total: int,
            amount_cents: int,
            original_expense_group_id: str,
            notes: str | None = None,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_card_expenses (
                credit_card_id,
                invoice_id,
                category_id,
                description,
                purchase_date,
                billing_date,
                installment_number,
                installment_total,
                amount_cents,
                original_expense_group_id,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                credit_card_id,
                invoice_id,
                category_id,
                description,
                purchase_date,
                billing_date,
                installment_number,
                installment_total,
                amount_cents,
                original_expense_group_id,
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
            SELECT COALESCE(SUM(e.amount_cents), 0) AS total_cents
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