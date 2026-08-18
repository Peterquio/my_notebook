from core.database.database_manager import (
    DatabaseManager,
)


class SubscriptionRepository:
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

    def criar_assinatura(
            self,
            name: str,
            amount_cents: int,
            charge_day: int,
            category_id: int,
            description: str | None = None,
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
                category_id,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                amount_cents,
                charge_day,
                category_id,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    # =========================================================
    # LISTAR
    # =========================================================

    def listar_assinaturas(
            self,
            include_inactive: bool = False,
    ) -> list[dict]:

        where = [
            "s.archived_at IS NULL",
        ]

        if not include_inactive:
            where.append(
                "s.is_active = 1"
            )

        where_sql = (
            "WHERE "
            + " AND ".join(where)
        )

        cursor = self.conexao.cursor()

        cursor.execute(
            f"""
            SELECT
                s.*,

                category.name AS category_name,
                category.color AS category_color

            FROM finance_subscriptions AS s

            LEFT JOIN finance_categories AS category
                ON category.id = s.category_id

            {where_sql}

            ORDER BY
                s.is_active DESC,
                s.charge_day ASC,
                s.name ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # =========================================================
    # BUSCAR
    # =========================================================

    def buscar_assinatura_por_id(
            self,
            subscription_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                s.*,

                category.name AS category_name,
                category.color AS category_color

            FROM finance_subscriptions AS s

            LEFT JOIN finance_categories AS category
                ON category.id = s.category_id

            WHERE s.id = ?

            LIMIT 1
            """,
            (
                subscription_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # =========================================================
    # ATUALIZAR
    # =========================================================

    def atualizar_assinatura(
            self,
            subscription_id: int,
            name: str,
            amount_cents: int,
            charge_day: int,
            category_id: int,
            description: str | None = None,
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
                category_id = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            """,
            (
                name,
                description,
                amount_cents,
                charge_day,
                category_id,
                notes,
                subscription_id,
            ),
        )

        self.conexao.commit()

    # =========================================================
    # STATUS
    # =========================================================

    def desativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:

        self.conexao.execute(
            """
            UPDATE finance_subscriptions
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                subscription_id,
            ),
        )

        self.conexao.commit()

    def reativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:

        self.conexao.execute(
            """
            UPDATE finance_subscriptions
            SET
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                subscription_id,
            ),
        )

        self.conexao.commit()

    # =========================================================
    # ARQUIVAR
    # =========================================================

    def arquivar_assinatura(
            self,
            subscription_id: int,
            archive_reason: str | None = None,
    ) -> None:

        self.conexao.execute(
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