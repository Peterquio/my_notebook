from core.database.database_manager import DatabaseManager


class FinanceCategoryRepository:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def listar_ativas(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                display_number,
                name,
                color,
                is_active,
                is_protected
            FROM finance_categories
            WHERE is_active = 1
            ORDER BY display_number ASC, name ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def criar(
            self,
            name: str,
            color: str,
            display_number: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_categories (
                display_number,
                name,
                color,
                is_active,
                is_protected
            )
            VALUES (?, ?, ?, 1, 0)
            """,
            (
                display_number,
                name,
                color,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def atualizar(
            self,
            category_id: int,
            name: str,
            color: str,
            display_number: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_categories
            SET
                name = ?,
                color = ?,
                display_number = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND is_protected = 0
            """,
            (
                name,
                color,
                display_number,
                category_id,
            ),
        )

        self.conexao.commit()

    def desativar(
            self,
            category_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_categories
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND is_protected = 0
            """,
            (category_id,),
        )

        self.conexao.commit()

    def obter_proximo_display_number(self) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COALESCE(MAX(display_number), 0) + 1 AS next_number
            FROM finance_categories
            WHERE is_active = 1
              AND display_number < 99
            """
        )

        row = cursor.fetchone()

        return int(row["next_number"])