from core.database.database_manager import DatabaseManager


class SubscriptionRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_assinatura(
            self,
            name: str,
            amount_cents: int,
            charge_day: int,
            payment_method: str,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            description: str | None = None,
            match_keywords: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_subscriptions (
                name,
                description,
                amount_cents,
                charge_day,
                payment_method,
                account_id,
                credit_card_id,
                match_keywords,
                start_date,
                end_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                amount_cents,
                charge_day,
                payment_method,
                account_id,
                credit_card_id,
                match_keywords,
                start_date,
                end_date,
                notes,
            ),
        )

        self.conexao.commit()
        return cursor.lastrowid

    def listar_assinaturas(
            self,
            include_inactive: bool = False,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        where_clauses = [
            "s.archived_at IS NULL",
        ]

        if not include_inactive:
            where_clauses.append(
                "s.is_active = 1"
            )

        where = (
            "WHERE "
            + " AND ".join(where_clauses)
        )

        cursor.execute(
            f"""
            SELECT
                s.*,
                a.name AS account_name,
                c.name AS credit_card_name
            FROM finance_subscriptions s
            LEFT JOIN finance_balance_accounts a
                ON a.id = s.account_id
            LEFT JOIN finance_credit_cards c
                ON c.id = s.credit_card_id
            {where}
            ORDER BY
                s.is_active DESC,
                s.charge_day ASC,
                s.name ASC
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def buscar_assinatura_por_id(
            self,
            subscription_id: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                s.*,
                a.name AS account_name,
                c.name AS credit_card_name
            FROM finance_subscriptions s
            LEFT JOIN finance_balance_accounts a
                ON a.id = s.account_id
            LEFT JOIN finance_credit_cards c
                ON c.id = s.credit_card_id
            WHERE s.id = ?
            LIMIT 1
            """,
            (subscription_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def atualizar_assinatura(
            self,
            subscription_id: int,
            name: str,
            amount_cents: int,
            charge_day: int,
            payment_method: str,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            description: str | None = None,
            match_keywords: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_subscriptions
            SET
                name = ?,
                description = ?,
                amount_cents = ?,
                charge_day = ?,
                payment_method = ?,
                account_id = ?,
                credit_card_id = ?,
                match_keywords = ?,
                start_date = ?,
                end_date = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                description,
                amount_cents,
                charge_day,
                payment_method,
                account_id,
                credit_card_id,
                match_keywords,
                start_date,
                end_date,
                notes,
                subscription_id,
            ),
        )

        self.conexao.commit()

    def desativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_subscriptions
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (subscription_id,),
        )

        self.conexao.commit()

    def reativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_subscriptions
            SET
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (subscription_id,),
        )

        self.conexao.commit()

    def arquivar_assinatura(
            self,
            subscription_id: int,
            archive_reason: str | None = None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_subscriptions
            SET
                is_active = 0,
                archived_at = CURRENT_TIMESTAMP,
                archive_reason = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                archive_reason,
                subscription_id,
            ),
        )

        self.conexao.commit()

    def criar_ou_atualizar_override(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
            expected_charge_date: str | None = None,
            expected_payment_date: str | None = None,
            amount_cents: int | None = None,
            status: str = "active",
            actual_charge_date: str | None = None,
            actual_amount_cents: int | None = None,
            resolved_at: str | None = None,
            resolution_type: str | None = None,
            matched_credit_card_expense_id: int | None = None,
            matched_balance_commitment_id: int | None = None,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        override = self.buscar_override_mes(
            subscription_id=subscription_id,
            reference_year=reference_year,
            reference_month=reference_month,
        )

        if override is None:
            cursor.execute(
                """
                INSERT INTO finance_subscription_overrides (
                    subscription_id,
                    reference_year,
                    reference_month,
                    expected_charge_date,
                    expected_payment_date,
                    amount_cents,
                    status,
                    actual_charge_date,
                    actual_amount_cents,
                    resolved_at,
                    resolution_type,
                    matched_credit_card_expense_id,
                    matched_balance_commitment_id,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    subscription_id,
                    reference_year,
                    reference_month,
                    expected_charge_date,
                    expected_payment_date,
                    amount_cents,
                    status,
                    actual_charge_date,
                    actual_amount_cents,
                    resolved_at,
                    resolution_type,
                    matched_credit_card_expense_id,
                    matched_balance_commitment_id,
                    notes,
                ),
            )

            self.conexao.commit()
            return cursor.lastrowid

        override_id = override["id"]

        cursor.execute(
            """
            UPDATE finance_subscription_overrides
            SET
                expected_charge_date = ?,
                expected_payment_date = ?,
                amount_cents = ?,
                status = ?,
                actual_charge_date = ?,
                actual_amount_cents = ?,
                resolved_at = ?,
                resolution_type = ?,
                matched_credit_card_expense_id = ?,
                matched_balance_commitment_id = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                expected_charge_date,
                expected_payment_date,
                amount_cents,
                status,
                actual_charge_date,
                actual_amount_cents,
                resolved_at,
                resolution_type,
                matched_credit_card_expense_id,
                matched_balance_commitment_id,
                notes,
                override_id,
            ),
        )

        self.conexao.commit()
        return override_id

    def buscar_override_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_subscription_overrides
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

    def excluir_override_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_subscription_overrides
            WHERE subscription_id = ?
              AND reference_year = ?
              AND reference_month = ?
            """,
            (
                subscription_id,
                reference_year,
                reference_month,
            ),
        )

        self.conexao.commit()

    def listar_overrides_periodo(
            self,
            start_year: int,
            start_month: int,
            end_year: int,
            end_month: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        start_key = start_year * 100 + start_month
        end_key = end_year * 100 + end_month

        cursor.execute(
            """
            SELECT *
            FROM finance_subscription_overrides
            WHERE (reference_year * 100 + reference_month) BETWEEN ? AND ?
            ORDER BY reference_year ASC, reference_month ASC
            """,
            (
                start_key,
                end_key,
            ),
        )

        return [dict(row) for row in cursor.fetchall()]