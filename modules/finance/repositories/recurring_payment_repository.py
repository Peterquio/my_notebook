from core.database.database_manager import (
    DatabaseManager,
)


class RecurringPaymentRepository:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.database = DatabaseManager(
            username
        )

        self.conexao = (
            self.database
            .get_connection()
        )

    # =========================================================
    # CRIAÇÃO
    # =========================================================

    def criar(
            self,
            reference_year: int,
            reference_month: int,
            payment_source: str,
            paid_amount_cents: int,
            paid_date: str,
            subscription_id: int | None = None,
            monthly_bill_id: int | None = None,
            pix_transaction_id: int | None = None,
            credit_card_expense_id: int | None = None,
            notes: str | None = None,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_recurring_payments (
                subscription_id,
                monthly_bill_id,
                reference_year,
                reference_month,
                payment_source,
                pix_transaction_id,
                credit_card_expense_id,
                paid_amount_cents,
                paid_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subscription_id,
                monthly_bill_id,
                reference_year,
                reference_month,
                payment_source,
                pix_transaction_id,
                credit_card_expense_id,
                paid_amount_cents,
                paid_date,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    # =========================================================
    # BUSCA POR ID
    # =========================================================

    def buscar_por_id(
            self,
            payment_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                payment.*,

                subscription.name
                    AS subscription_name,

                monthly_bill.name
                    AS monthly_bill_name

            FROM finance_recurring_payments AS payment

            LEFT JOIN finance_subscriptions AS subscription
                ON subscription.id =
                   payment.subscription_id

            LEFT JOIN finance_monthly_templates AS monthly_bill
                ON monthly_bill.id =
                   payment.monthly_bill_id

            WHERE payment.id = ?

            LIMIT 1
            """,
            (
                payment_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # ASSINATURA / MÊS
    # =========================================================

    def buscar_assinatura_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_recurring_payments

            WHERE subscription_id = ?
              AND reference_year = ?
              AND reference_month = ?

            LIMIT 1
            """,
            (
                subscription_id,
                reference_year,
                reference_month,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # CONTA DO MÊS / MÊS
    # =========================================================

    def buscar_conta_mes(
            self,
            monthly_bill_id: int,
            reference_year: int,
            reference_month: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_recurring_payments

            WHERE monthly_bill_id = ?
              AND reference_year = ?
              AND reference_month = ?

            LIMIT 1
            """,
            (
                monthly_bill_id,
                reference_year,
                reference_month,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # BUSCA PELO PIX
    # =========================================================

    def buscar_por_pix(
            self,
            pix_transaction_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_recurring_payments

            WHERE pix_transaction_id = ?

            LIMIT 1
            """,
            (
                pix_transaction_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # BUSCA PELO CARTÃO
    # =========================================================

    def buscar_por_lancamento_cartao(
            self,
            credit_card_expense_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_recurring_payments

            WHERE credit_card_expense_id = ?

            LIMIT 1
            """,
            (
                credit_card_expense_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # LISTAGEM POR MÊS
    # =========================================================

    def listar_mes(
            self,
            reference_year: int,
            reference_month: int,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                payment.*,

                subscription.name
                    AS subscription_name,

                monthly_bill.name
                    AS monthly_bill_name

            FROM finance_recurring_payments AS payment

            LEFT JOIN finance_subscriptions AS subscription
                ON subscription.id =
                   payment.subscription_id

            LEFT JOIN finance_monthly_templates AS monthly_bill
                ON monthly_bill.id =
                   payment.monthly_bill_id

            WHERE payment.reference_year = ?
              AND payment.reference_month = ?

            ORDER BY
                payment.paid_date ASC,
                payment.id ASC
            """,
            (
                reference_year,
                reference_month,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # =========================================================
    # EXCLUSÃO
    # =========================================================

    def excluir(
            self,
            payment_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_recurring_payments
            WHERE id = ?
            """,
            (
                payment_id,
            ),
        )

        self.conexao.commit()

    def excluir_por_pix(
            self,
            pix_transaction_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_recurring_payments
            WHERE pix_transaction_id = ?
            """,
            (
                pix_transaction_id,
            ),
        )

        self.conexao.commit()

    def excluir_por_lancamento_cartao(
            self,
            credit_card_expense_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_recurring_payments
            WHERE credit_card_expense_id = ?
            """,
            (
                credit_card_expense_id,
            ),
        )

        self.conexao.commit()