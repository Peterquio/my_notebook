from core.database.database_manager import DatabaseManager


class CreditCardRepository:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def listar_assets(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                bank_name,
                asset_name,
                preset_key
            FROM finance_credit_card_assets
            WHERE is_active = 1
            ORDER BY bank_name, asset_name
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def criar_cartao(
            self,
            dashboard_card_id: str,
            name: str,
            asset_id: str,
            limit_amount_cents: int,
            closing_day: int,
            due_day: int,
            last_four_digits: str | None = None,
            account_id: int | None = None,
            sync_with_balance: bool = False,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_cards (
                dashboard_card_id,
                name,
                asset_id,
                limit_amount_cents,
                closing_day,
                due_day,
                last_four_digits,
                account_id,
                sync_with_balance
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dashboard_card_id,
                name,
                asset_id,
                limit_amount_cents,
                closing_day,
                due_day,
                last_four_digits,
                account_id,
                int(sync_with_balance),
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def buscar_por_dashboard_card_id(
            self,
            dashboard_card_id: str,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                cc.id,
                cc.dashboard_card_id,
                cc.name,
                cc.asset_id,
                cc.limit_amount_cents,
                cc.closing_day,
                cc.due_day,
                cc.last_four_digits,
                cc.account_id,
                cc.sync_with_balance,

                a.bank_name,
                a.asset_name,
                a.preset_key
            FROM finance_credit_cards cc
            INNER JOIN finance_credit_card_assets a
                ON a.id = cc.asset_id
            WHERE cc.dashboard_card_id = ?
              AND cc.is_active = 1
            """,
            (dashboard_card_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def listar_cartoes_ativos(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT cc.id,
                   cc.dashboard_card_id,
                   cc.name,
                   cc.asset_id,
                   cc.limit_amount_cents,
                   cc.closing_day,
                   cc.due_day,
                   cc.last_four_digits,
                   cc.account_id,
                   cc.sync_with_balance,

                   a.bank_name,
                   a.asset_name,
                   a.preset_key
            FROM finance_credit_cards cc
                     INNER JOIN finance_credit_card_assets a
                                ON a.id = cc.asset_id
            WHERE cc.is_active = 1
            ORDER BY cc.created_at DESC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]