from core.database.database_manager import DatabaseManager


class CreditCardInvoiceRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def buscar_por_cartao_mes(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_invoices
            WHERE credit_card_id = ?
              AND invoice_year = ?
              AND invoice_month = ?
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def criar_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
            closing_date: str,
            due_date: str,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_card_invoices (
                credit_card_id,
                invoice_year,
                invoice_month,
                closing_date,
                due_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
                closing_date,
                due_date,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid