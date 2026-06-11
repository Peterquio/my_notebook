from core.database.database_manager import DatabaseManager


class FinanceSettingsRepository:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.db = DatabaseManager(username)

    def obter_reference_day(self) -> int:
        conn = self.db.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT finance_reference_day
                FROM app_settings
                WHERE id = 1
            """)

            row = cursor.fetchone()

            if row is None:
                return 1

            return row["finance_reference_day"] or 1

        finally:
            conn.close()

    def salvar_reference_day(
            self,
            day: int,
    ) -> None:
        conn = self.db.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE app_settings
                SET finance_reference_day = ?
                WHERE id = 1
            """, (day,))

            conn.commit()

        finally:
            conn.close()