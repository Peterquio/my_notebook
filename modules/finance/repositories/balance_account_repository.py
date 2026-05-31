from core.database.database_manager import DatabaseManager


class BalanceAccountRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_conta(
            self,
            name: str,
            account_type: str = "bank",
            include_in_global_balance: bool = True,
            is_investment: bool = False,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_accounts (
                name,
                account_type,
                include_in_global_balance,
                is_investment
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                account_type,
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
                name,
                account_type,
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
                name,
                account_type,
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

    def definir_saldo_inicial_conta(
            self,
            cycle_id: int,
            account_id: int,
            opening_balance_cents: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_cycle_account_openings (
                cycle_id,
                account_id,
                opening_balance_cents
            )
            VALUES (?, ?, ?)
            ON CONFLICT(cycle_id, account_id)
            DO UPDATE SET
                opening_balance_cents = excluded.opening_balance_cents,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                cycle_id,
                account_id,
                opening_balance_cents,
            ),
        )

        self.conexao.commit()

    def listar_saldos_iniciais_ciclo(
            self,
            cycle_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                o.id,
                o.cycle_id,
                o.account_id,
                o.opening_balance_cents,

                a.name AS account_name,
                a.account_type,
                a.include_in_global_balance,
                a.is_investment
            FROM finance_balance_cycle_account_openings o
            INNER JOIN finance_balance_accounts a
                ON a.id = o.account_id
            WHERE o.cycle_id = ?
              AND a.is_active = 1
            ORDER BY a.name
            """,
            (cycle_id,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def atualizar_conta(
            self,
            account_id: int,
            name: str,
            account_type: str,
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
                include_in_global_balance = ?,
                is_investment = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                account_type,
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