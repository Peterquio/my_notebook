import json

from core.database.database_manager import DatabaseManager


class DashboardCardRepository:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_card(
            self,
            module_name: str,
            card_data: dict,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO dashboard_cards (
                card_id,
                module_name,
                card_type,
                title,
                size,
                config_json,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                card_data["id"],
                module_name,
                card_data["card_type"],
                card_data.get("title"),
                card_data.get("size"),
                json.dumps(
                    card_data.get("config", {}),
                    ensure_ascii=False,
                ),
            ),
        )

        self.conexao.commit()

    def listar_cards(
            self,
            module_name: str,
            active_only: bool = False,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        query = """
            SELECT *
            FROM dashboard_cards
            WHERE module_name = ?
        """

        params = [module_name]

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY created_at ASC"

        cursor.execute(query, params)

        cards = []

        for row in cursor.fetchall():
            item = dict(row)

            item["config"] = json.loads(
                item.pop("config_json") or "{}"
            )

            cards.append(item)

        return cards

    def atualizar_status_card(
            self,
            card_id: str,
            is_active: bool,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE dashboard_cards
            SET is_active = ?
            WHERE card_id = ?
            """,
            (
                int(is_active),
                card_id,
            ),
        )

        self.conexao.commit()

    def excluir_card(
            self,
            card_id: str,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM dashboard_cards
            WHERE card_id = ?
            """,
            (card_id,),
        )

        self.conexao.commit()

    def listar_cards_removidos(
            self,
            module_name: str,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                card_id AS id,
                module_name,
                card_type,
                title,
                size,
                config_json,
                is_active
            FROM dashboard_cards
            WHERE module_name = ?
              AND is_active = 0
            ORDER BY updated_at DESC, created_at DESC
            """,
            (module_name,),
        )

        cards = []

        for row in cursor.fetchall():
            item = dict(row)

            item["config"] = json.loads(
                item.pop("config_json") or "{}"
            )

            cards.append(item)


        return cards

    def excluir_card_definitivamente(
            self,
            card_id: str,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM dashboard_layouts
            WHERE card_id = ?
            """,
            (card_id,),
        )

        cursor.execute(
            """
            DELETE FROM dashboard_cards
            WHERE card_id = ?
            """,
            (card_id,),
        )

        self.conexao.commit()