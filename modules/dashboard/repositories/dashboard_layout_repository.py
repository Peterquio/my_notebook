from sqlite3 import Connection


class DashboardLayoutRepository:
    def __init__(self, conexao: Connection):
        self.conexao = conexao

    def salvar_layout(
        self,
        module_name: str,
        layout_items: list[dict],
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM dashboard_layouts
            WHERE module_name = ?
            """,
            (module_name,),
        )

        for index, item in enumerate(layout_items):
            cursor.execute(
                """
                INSERT INTO dashboard_layouts (
                    module_name,
                    card_id,
                    row,
                    column,
                    width_units,
                    height_units,
                    sort_order
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    module_name,
                    item["card_id"],
                    item["row"],
                    item["column"],
                    item["width_units"],
                    item["height_units"],
                    index,
                ),
            )

        self.conexao.commit()

    def listar_layout(
        self,
        module_name: str,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                card_id,
                row,
                column,
                width_units,
                height_units,
                sort_order
            FROM dashboard_layouts
            WHERE module_name = ?
            ORDER BY sort_order ASC
            """,
            (module_name,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]