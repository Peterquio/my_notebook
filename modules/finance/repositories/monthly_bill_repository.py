from core.database.database_manager import (
    DatabaseManager,
)


class MonthlyBillRepository:
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
    # CRIAR
    # =========================================================

    def criar(
            self,
            name: str,
            estimated_amount_cents: int,
            due_day: int,
            preferred_payment_method: str | None = None,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            category_id: int | None = None,
            description: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_monthly_templates (
                name,
                description,
                estimated_amount_cents,
                due_day,
                preferred_payment_method,
                account_id,
                credit_card_id,
                category_id,
                start_date,
                end_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                estimated_amount_cents,
                due_day,
                preferred_payment_method,
                account_id,
                credit_card_id,
                category_id,
                start_date,
                end_date,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    # =========================================================
    # BUSCAR
    # =========================================================

    def buscar_por_id(
            self,
            monthly_bill_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                bill.*,

                account.name AS account_name,
                card.name AS credit_card_name,
                category.name AS category_name

            FROM finance_monthly_templates AS bill

            LEFT JOIN finance_balance_accounts AS account
                ON account.id = bill.account_id

            LEFT JOIN finance_credit_cards AS card
                ON card.id = bill.credit_card_id

            LEFT JOIN finance_categories AS category
                ON category.id = bill.category_id

            WHERE bill.id = ?

            LIMIT 1
            """,
            (
                monthly_bill_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # LISTAR
    # =========================================================

    def listar(
            self,
            include_inactive: bool = False,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        where = [
            "bill.archived_at IS NULL",
        ]

        if not include_inactive:
            where.append(
                "bill.is_active = 1"
            )

        where_sql = (
            " WHERE "
            + " AND ".join(where)
        )

        cursor.execute(
            f"""
            SELECT
                bill.*,

                account.name AS account_name,
                card.name AS credit_card_name,
                category.name AS category_name

            FROM finance_monthly_templates AS bill

            LEFT JOIN finance_balance_accounts AS account
                ON account.id = bill.account_id

            LEFT JOIN finance_credit_cards AS card
                ON card.id = bill.credit_card_id

            LEFT JOIN finance_categories AS category
                ON category.id = bill.category_id

            {where_sql}

            ORDER BY
                bill.is_active DESC,
                bill.due_day ASC,
                bill.name ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # =========================================================
    # ATUALIZAR
    # =========================================================

    def atualizar(
            self,
            monthly_bill_id: int,
            name: str,
            estimated_amount_cents: int,
            due_day: int,
            preferred_payment_method: str | None = None,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            category_id: int | None = None,
            description: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_monthly_templates
            SET
                name = ?,
                description = ?,
                estimated_amount_cents = ?,
                due_day = ?,
                preferred_payment_method = ?,
                account_id = ?,
                credit_card_id = ?,
                category_id = ?,
                start_date = ?,
                end_date = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            """,
            (
                name,
                description,
                estimated_amount_cents,
                due_day,
                preferred_payment_method,
                account_id,
                credit_card_id,
                category_id,
                start_date,
                end_date,
                notes,
                monthly_bill_id,
            ),
        )

        self.conexao.commit()

    # =========================================================
    # STATUS
    # =========================================================

    def desativar(
            self,
            monthly_bill_id: int,
    ) -> None:

        self.conexao.execute(
            """
            UPDATE finance_monthly_templates
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                monthly_bill_id,
            ),
        )

        self.conexao.commit()

    def reativar(
            self,
            monthly_bill_id: int,
    ) -> None:

        self.conexao.execute(
            """
            UPDATE finance_monthly_templates
            SET
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                monthly_bill_id,
            ),
        )

        self.conexao.commit()

    def arquivar(
            self,
            monthly_bill_id: int,
            archive_reason: str | None = None,
    ) -> None:

        self.conexao.execute(
            """
            UPDATE finance_monthly_templates
            SET
                is_active = 0,
                archived_at = CURRENT_TIMESTAMP,
                archive_reason = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                archive_reason,
                monthly_bill_id,
            ),
        )

        self.conexao.commit()