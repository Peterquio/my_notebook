from core.database.database_manager import DatabaseManager


class CreditCardImportBatchRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_lote(
            self,
            credit_card_id: int,
            source_name: str,
            source_file_name: str,
            total_expenses: int = 0,
            total_adjustments: int = 0,
    ) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_card_import_batches (
                credit_card_id,
                source_name,
                source_file_name,
                total_expenses,
                total_adjustments
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                credit_card_id,
                source_name,
                source_file_name,
                total_expenses,
                total_adjustments,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid