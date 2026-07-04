import json

from core.database.database_manager import DatabaseManager


class CalculatorRepository:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_simulacao(
            self,
            name: str,
            simulation_type: str,
            period_mode: str,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_calculator_simulations (
                name,
                simulation_type,
                period_mode,
                start_date,
                end_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                simulation_type,
                period_mode,
                start_date,
                end_date,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def listar_simulacoes(
            self,
            active_only: bool = True,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        query = """
            SELECT *
            FROM finance_calculator_simulations
        """

        params = []

        if active_only:
            query += " WHERE is_active = 1"

        query += " ORDER BY updated_at DESC, created_at DESC"

        cursor.execute(query, params)

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def buscar_simulacao(
            self,
            simulation_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_calculator_simulations
            WHERE id = ?
            """,
            (simulation_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def atualizar_simulacao(
            self,
            simulation_id: int,
            name: str,
            simulation_type: str,
            period_mode: str,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_calculator_simulations
            SET
                name = ?,
                simulation_type = ?,
                period_mode = ?,
                start_date = ?,
                end_date = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                simulation_type,
                period_mode,
                start_date,
                end_date,
                notes,
                simulation_id,
            ),
        )

        self.conexao.commit()

    def desativar_simulacao(
            self,
            simulation_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_calculator_simulations
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (simulation_id,),
        )

        self.conexao.commit()

    def excluir_simulacao_definitivamente(
            self,
            simulation_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_calculator_simulation_items
            WHERE simulation_id = ?
            """,
            (simulation_id,),
        )

        cursor.execute(
            """
            DELETE FROM finance_calculator_simulations
            WHERE id = ?
            """,
            (simulation_id,),
        )

        self.conexao.commit()

    def criar_item(
            self,
            simulation_id: int,
            title: str,
            kind: str,
            item_date: str | None,
            amount_cents: int,
            sort_order: int = 0,
            notes: str | None = None,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_calculator_simulation_items (
                simulation_id,
                title,
                kind,
                item_date,
                amount_cents,
                sort_order,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                simulation_id,
                title,
                kind,
                item_date,
                amount_cents,
                sort_order,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def listar_itens(
            self,
            simulation_id: int,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_calculator_simulation_items
            WHERE simulation_id = ?
            ORDER BY
                item_date IS NULL,
                item_date ASC,
                sort_order ASC,
                id ASC
            """,
            (simulation_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def atualizar_item(
            self,
            item_id: int,
            title: str,
            kind: str,
            item_date: str | None,
            amount_cents: int,
            sort_order: int = 0,
            notes: str | None = None,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_calculator_simulation_items
            SET
                title = ?,
                kind = ?,
                item_date = ?,
                amount_cents = ?,
                sort_order = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                title,
                kind,
                item_date,
                amount_cents,
                sort_order,
                notes,
                item_id,
            ),
        )

        self.conexao.commit()

    def excluir_item(
            self,
            item_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_calculator_simulation_items
            WHERE id = ?
            """,
            (item_id,),
        )

        self.conexao.commit()