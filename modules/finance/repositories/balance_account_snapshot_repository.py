from core.database.database_manager import DatabaseManager


class BalanceAccountSnapshotRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_snapshot(
            self,
            account_id: int,
            snapshot_date: str,
            balance_cents: int,
            snapshot_type: str = "manual",
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_account_snapshots (
                account_id,
                snapshot_date,
                balance_cents,
                snapshot_type,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                account_id,
                snapshot_date,
                balance_cents,
                snapshot_type,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def buscar_snapshot_mais_recente_ate_data(
            self,
            account_id: int,
            data_iso: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_account_snapshots
            WHERE account_id = ?
              AND snapshot_date <= ?
            ORDER BY snapshot_date DESC, id DESC
            LIMIT 1
            """,
            (
                account_id,
                data_iso,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def listar_snapshots_conta(
            self,
            account_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_account_snapshots
            WHERE account_id = ?
            ORDER BY snapshot_date DESC, id DESC
            """,
            (
                account_id,
            ),
        )

        return [dict(row) for row in cursor.fetchall()]