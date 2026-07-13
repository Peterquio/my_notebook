from core.database.database_manager import DatabaseManager


class FinanceGraphRepository:
    INTERNAL_TRANSFER_ORIGIN = "internal_transfer"

    CREDIT_CARD_COMMITMENT_ORIGINS = {
        "credit_card_open",
        "credit_card_projected",
        "credit_card_closed",
    }

    def __init__(
            self,
            username: str,
    ) -> None:

        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def listar_receitas_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                r.id,
                r.account_id,
                r.category_id,
                r.description,

                CASE
                    WHEN r.status = 'received'
                         AND r.received_date IS NOT NULL
                    THEN r.received_date
                    ELSE r.expected_date
                END AS event_date,

                CASE
                    WHEN r.status = 'received'
                         AND r.actual_amount_cents IS NOT NULL
                    THEN r.actual_amount_cents
                    ELSE r.expected_amount_cents
                END AS amount_cents,

                r.status,
                r.commitment_origin,
                r.projection_type,

                c.name AS category_name,
                c.color AS category_color

            FROM finance_balance_income_entries r

            LEFT JOIN finance_categories c
                ON c.id = r.category_id

            WHERE
                CASE
                    WHEN r.status = 'received'
                         AND r.received_date IS NOT NULL
                    THEN r.received_date
                    ELSE r.expected_date
                END BETWEEN ? AND ?

                AND COALESCE(
                    r.commitment_origin,
                    ''
                ) != ?

            ORDER BY
                event_date ASC,
                r.id ASC
            """,
            (
                start_date,
                end_date,
                self.INTERNAL_TRANSFER_ORIGIN,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_compromissos_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        placeholders_cartao = ", ".join(
            "?"
            for _ in self.CREDIT_CARD_COMMITMENT_ORIGINS
        )

        origens_cartao = tuple(
            self.CREDIT_CARD_COMMITMENT_ORIGINS
        )

        parametros = (
            start_date,
            end_date,
            self.INTERNAL_TRANSFER_ORIGIN,
            *origens_cartao,
        )

        cursor.execute(
            f"""
            SELECT
                b.id,
                b.account_id,
                b.credit_card_id,
                b.category_id,
                b.description,

                CASE
                    WHEN b.status = 'paid'
                         AND b.paid_date IS NOT NULL
                    THEN b.paid_date
                    ELSE b.due_date
                END AS event_date,

                CASE
                    WHEN b.status = 'paid'
                         AND b.actual_amount_cents IS NOT NULL
                    THEN b.actual_amount_cents
                    ELSE b.expected_amount_cents
                END AS amount_cents,

                b.status,
                b.payment_type,
                b.commitment_origin,
                b.projection_type,
                b.external_reference,

                c.name AS category_name,
                c.color AS category_color

            FROM finance_balance_commitments b

            LEFT JOIN finance_categories c
                ON c.id = b.category_id

            WHERE
                CASE
                    WHEN b.status = 'paid'
                         AND b.paid_date IS NOT NULL
                    THEN b.paid_date
                    ELSE b.due_date
                END BETWEEN ? AND ?

                AND COALESCE(
                    b.commitment_origin,
                    ''
                ) != ?

                AND COALESCE(
                    b.commitment_origin,
                    ''
                ) NOT IN ({placeholders_cartao})

                AND COALESCE(
                    b.payment_type,
                    ''
                ) != 'credit_card'

            ORDER BY
                event_date ASC,
                b.id ASC
            """,
            parametros,
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_despesas_cartao_por_vencimento(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.id AS expense_id,
                e.credit_card_id,
                e.invoice_id,
                e.category_id,

                e.effective_description AS description,
                e.effective_purchase_date,
                e.effective_amount_cents AS amount_cents,

                e.installment_number,
                e.installment_total,
                e.source_type,
                e.source_reference,

                i.invoice_year,
                i.invoice_month,
                i.due_date AS event_date,

                c.name AS category_name,
                c.color AS category_color

            FROM finance_credit_card_expenses e

            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            LEFT JOIN finance_categories c
                ON c.id = e.category_id

            WHERE i.due_date BETWEEN ? AND ?
              AND e.status != 'cancelled'
              AND e.effective_amount_cents > 0

            ORDER BY
                i.due_date ASC,
                e.id ASC
            """,
            (
                start_date,
                end_date,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_despesas_cartao_sem_fatura(
            self,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.id AS expense_id,
                e.credit_card_id,
                e.invoice_id,
                e.category_id,

                e.effective_description AS description,
                e.effective_purchase_date,
                e.effective_amount_cents AS amount_cents,

                e.installment_number,
                e.installment_total,
                e.source_type,
                e.source_reference,

                cc.closing_day,
                cc.due_day,

                c.name AS category_name,
                c.color AS category_color

            FROM finance_credit_card_expenses e

            INNER JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            LEFT JOIN finance_categories c
                ON c.id = e.category_id

            WHERE e.invoice_id IS NULL
              AND e.status != 'cancelled'
              AND e.effective_amount_cents > 0
              AND cc.is_active = 1

            ORDER BY
                e.effective_purchase_date ASC,
                e.id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]