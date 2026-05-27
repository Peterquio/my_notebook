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

    def atualizar_categoria(
            self,
            expense_id: int,
            category_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                category_id = ?
            WHERE id = ?
            """,
            (
                category_id,
                expense_id,
            ),
        )

        self.conexao.commit()

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
            sort_mode: str = "categoria",
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        order_by_options = {
            "data": """
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "categoria": """
                c.display_number ASC,
                e.installment_number ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "alfabetica": """
                e.effective_description ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "valor": """
                e.effective_amount_cents DESC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "parcelas": """
                CASE
                    WHEN e.installment_total > 1 THEN 0
                    ELSE 1
                END ASC,
                e.installment_number DESC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
        }

        order_by = order_by_options.get(
            sort_mode,
            order_by_options["categoria"],
        )

        cursor.execute(
            """
            SELECT
                e.id AS expense_id,
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
            """ + order_by,
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
            ORDER BY effective_purchase_date
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

    def existe_lancamento_importado(
            self,
            credit_card_id: int,
            original_description: str,
            original_purchase_date: str,
            original_amount_cents: int,
            installment_number: int,
            installment_total: int,
    ) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND original_description = ?
              AND original_purchase_date = ?
              AND original_amount_cents = ?
              AND installment_number = ?
              AND installment_total = ?
              AND status != 'cancelled'
            LIMIT 1
            """,
            (
                credit_card_id,
                original_description,
                original_purchase_date,
                original_amount_cents,
                installment_number,
                installment_total,
            ),
        )

        return cursor.fetchone() is not None

    def contar_lancamentos_por_assinatura(
            self,
            credit_card_id: int,
            original_description: str,
            original_purchase_date: str,
            original_amount_cents: int,
            installment_number: int,
            installment_total: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND original_description = ?
              AND original_purchase_date = ?
              AND original_amount_cents = ?
              AND installment_number = ?
              AND installment_total = ?
              AND status != 'cancelled'
            """,
            (
                credit_card_id,
                original_description,
                original_purchase_date,
                original_amount_cents,
                installment_number,
                installment_total,
            ),
        )

        row = cursor.fetchone()

        return int(row["total"] or 0)

    def atualizar_lancamento(
            self,
            expense_id: int,
            invoice_id: int,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
            notes: str | None = None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                invoice_id = ?,
                category_id = ?,
                effective_description = ?,
                effective_purchase_date = ?,
                effective_amount_cents = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status != 'cancelled'
            """,
            (
                invoice_id,
                category_id,
                effective_description,
                effective_purchase_date,
                effective_amount_cents,
                notes,
                expense_id,
            ),
        )

        self.conexao.commit()