from core.database.database_manager import DatabaseManager


class MonthlyTemplateRepository:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_template(
            self,
            template_type: str,
            description: str,
            estimated_amount_cents: int,
            day_of_month: int,
            account_id: int | None = None,
            category_id: int | None = None,
            payment_type: str = "bank_account",
            credit_card_id: int | None = None,
            external_reference: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            auto_materialize: bool = True,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_monthly_templates (
                template_type,
                description,
                estimated_amount_cents,
                day_of_month,
                account_id,
                category_id,
                payment_type,
                credit_card_id,
                external_reference,
                start_date,
                end_date,
                auto_materialize,
                is_active,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                template_type,
                description,
                estimated_amount_cents,
                day_of_month,
                account_id,
                category_id,
                payment_type,
                credit_card_id,
                external_reference,
                start_date,
                end_date,
                int(auto_materialize),
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def atualizar_template(
            self,
            template_id: int,
            template_type: str,
            description: str,
            estimated_amount_cents: int,
            day_of_month: int,
            account_id: int | None = None,
            category_id: int | None = None,
            payment_type: str = "bank_account",
            credit_card_id: int | None = None,
            external_reference: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            auto_materialize: bool = True,
            notes: str | None = None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_monthly_templates
            SET
                template_type = ?,
                description = ?,
                estimated_amount_cents = ?,
                day_of_month = ?,
                account_id = ?,
                category_id = ?,
                payment_type = ?,
                credit_card_id = ?,
                external_reference = ?,
                start_date = ?,
                end_date = ?,
                auto_materialize = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                template_type,
                description,
                estimated_amount_cents,
                day_of_month,
                account_id,
                category_id,
                payment_type,
                credit_card_id,
                external_reference,
                start_date,
                end_date,
                int(auto_materialize),
                notes,
                template_id,
            ),
        )

        self.conexao.commit()

    def buscar_por_id(
            self,
            template_id: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_monthly_templates
            WHERE id = ?
            LIMIT 1
            """,
            (template_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def buscar_por_external_reference(
            self,
            external_reference: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_monthly_templates
            WHERE external_reference = ?
            LIMIT 1
            """,
            (external_reference,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def listar_todos(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_monthly_templates
            ORDER BY
                is_active DESC,
                template_type ASC,
                day_of_month ASC,
                description ASC
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def listar_ativos(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_monthly_templates
            WHERE is_active = 1
            ORDER BY
                template_type ASC,
                day_of_month ASC,
                description ASC
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def listar_por_tipo(
            self,
            template_type: str,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_monthly_templates
            WHERE template_type = ?
              AND is_active = 1
            ORDER BY
                day_of_month ASC,
                description ASC
            """,
            (template_type,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def desativar_template(
            self,
            template_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_monthly_templates
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (template_id,),
        )

        self.conexao.commit()

    def reativar_template(
            self,
            template_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_monthly_templates
            SET
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (template_id,),
        )

        self.conexao.commit()