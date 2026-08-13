from core.database.database_manager import DatabaseManager


class BalanceAccountRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_conta(
            self,
            name: str,
            account_type: str = "bank",
            institution_name: str | None = None,
            bank_preset_key: str | None = None,
            agency: str | None = None,
            account_number: str | None = None,
            account_kind: str | None = None,
            include_in_global_balance: bool = True,
            is_investment: bool = False,
            dashboard_card_id: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_accounts (
                dashboard_card_id,
                name,
                account_type,
                institution_name,
                bank_preset_key,
                agency,
                account_number,
                account_kind,
                include_in_global_balance,
                is_investment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dashboard_card_id,
                name,
                account_type,
                institution_name,
                bank_preset_key,
                agency,
                account_number,
                account_kind,
                int(include_in_global_balance),
                int(is_investment),
            ),
        )

        self.conexao.commit()
        return cursor.lastrowid

    def listar_contas_ativas(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                dashboard_card_id,
                name,
                account_type,
                institution_name,
                bank_preset_key,
                agency,
                account_number,
                account_kind,
                include_in_global_balance,
                is_investment,
                is_active,
                created_at,
                updated_at
            FROM finance_balance_accounts
            WHERE is_active = 1
            ORDER BY name
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def buscar_conta_por_id(
            self,
            account_id: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                dashboard_card_id,
                name,
                account_type,
                institution_name,
                bank_preset_key,
                agency,
                account_number,
                account_kind,
                include_in_global_balance,
                is_investment,
                is_active,
                created_at,
                updated_at
            FROM finance_balance_accounts
            WHERE id = ?
            """,
            (account_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def buscar_conta_por_dashboard_card_id(
            self,
            dashboard_card_id: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                dashboard_card_id,
                name,
                account_type,
                institution_name,
                bank_preset_key,
                agency,
                account_number,
                account_kind,
                include_in_global_balance,
                is_investment,
                is_active,
                created_at,
                updated_at
            FROM finance_balance_accounts
            WHERE dashboard_card_id = ?
              AND is_active = 1
            """,
            (dashboard_card_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def atualizar_conta(
            self,
            account_id: int,
            name: str,
            account_type: str,
            institution_name: str | None,
            bank_preset_key: str | None,
            agency: str | None,
            account_number: str | None,
            account_kind: str | None,
            include_in_global_balance: bool,
            is_investment: bool,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_accounts
            SET
                name = ?,
                account_type = ?,
                institution_name = ?,
                bank_preset_key = ?,
                agency = ?,
                account_number = ?,
                account_kind = ?,
                include_in_global_balance = ?,
                is_investment = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                account_type,
                institution_name,
                bank_preset_key,
                agency,
                account_number,
                account_kind,
                int(include_in_global_balance),
                int(is_investment),
                account_id,
            ),
        )

        self.conexao.commit()

    def desativar_conta(
            self,
            account_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_accounts
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (account_id,),
        )

        self.conexao.commit()