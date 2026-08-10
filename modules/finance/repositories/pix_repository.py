from core.database.database_manager import DatabaseManager


class PixRepository:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_transacao(
            self,
            account_id: int,
            transaction_type: str,
            amount_cents: int,
            transaction_date: str,
            contact_id: int | None = None,
            contact_name: str | None = None,
            category_id: int = 1,
            description: str | None = None,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_pix_transactions (
                account_id,
                transaction_type,
                amount_cents,
                transaction_date,
                contact_id,
                contact_name,
                category_id,
                description,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                account_id,
                transaction_type,
                amount_cents,
                transaction_date,
                contact_id,
                contact_name,
                category_id,
                description,
                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def listar_transacoes(
            self,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                pix.id,

                pix.account_id,
                account.name AS account_name,
                account.institution_name AS account_institution,

                pix.transaction_type,
                pix.amount_cents,
                pix.transaction_date,

                pix.contact_id,
                pix.contact_name,

                pix.category_id,
                category.name AS category_name,
                category.color AS category_color,

                pix.description,
                pix.notes,

                pix.created_at,
                pix.updated_at

            FROM finance_pix_transactions AS pix

            INNER JOIN finance_balance_accounts AS account
                ON account.id = pix.account_id

            LEFT JOIN finance_categories AS category
                ON category.id = pix.category_id

            ORDER BY
                pix.transaction_date DESC,
                pix.id DESC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_transacoes_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                pix.id,

                pix.account_id,
                account.name AS account_name,
                account.institution_name AS account_institution,

                pix.transaction_type,
                pix.amount_cents,
                pix.transaction_date,

                pix.contact_id,
                pix.contact_name,

                pix.category_id,
                category.name AS category_name,
                category.color AS category_color,

                pix.description,
                pix.notes,

                pix.created_at,
                pix.updated_at

            FROM finance_pix_transactions AS pix

            INNER JOIN finance_balance_accounts AS account
                ON account.id = pix.account_id

            LEFT JOIN finance_categories AS category
                ON category.id = pix.category_id

            WHERE pix.transaction_date BETWEEN ? AND ?

            ORDER BY
                pix.transaction_date DESC,
                pix.id DESC
            """,
            (
                start_date,
                end_date,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def buscar_transacao_por_id(
            self,
            transaction_id: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                pix.id,

                pix.account_id,
                account.name AS account_name,
                account.institution_name AS account_institution,

                pix.transaction_type,
                pix.amount_cents,
                pix.transaction_date,

                pix.contact_id,
                pix.contact_name,

                pix.category_id,
                category.name AS category_name,
                category.color AS category_color,

                pix.description,
                pix.notes,

                pix.created_at,
                pix.updated_at

            FROM finance_pix_transactions AS pix

            INNER JOIN finance_balance_accounts AS account
                ON account.id = pix.account_id

            LEFT JOIN finance_categories AS category
                ON category.id = pix.category_id

            WHERE pix.id = ?
            """,
            (
                transaction_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def atualizar_transacao(
            self,
            transaction_id: int,
            account_id: int,
            transaction_type: str,
            amount_cents: int,
            transaction_date: str,
            contact_id: int | None = None,
            contact_name: str | None = None,
            category_id: int = 1,
            description: str | None = None,
            notes: str | None = None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_pix_transactions
            SET
                account_id = ?,
                transaction_type = ?,
                amount_cents = ?,
                transaction_date = ?,
                contact_id = ?,
                contact_name = ?,
                category_id = ?,
                description = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
            """,
            (
                account_id,
                transaction_type,
                amount_cents,
                transaction_date,
                contact_id,
                contact_name,
                category_id,
                description,
                notes,
                transaction_id,
            ),
        )

        self.conexao.commit()

    def excluir_transacao(
            self,
            transaction_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_pix_transactions
            WHERE id = ?
            """,
            (
                transaction_id,
            ),
        )

        self.conexao.commit()

    def obter_resumo_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> dict:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_transactions,

                COALESCE(
                    SUM(
                        CASE
                            WHEN transaction_type = 'received'
                            THEN amount_cents
                            ELSE 0
                        END
                    ),
                    0
                ) AS received_cents,

                COALESCE(
                    SUM(
                        CASE
                            WHEN transaction_type = 'sent'
                            THEN amount_cents
                            ELSE 0
                        END
                    ),
                    0
                ) AS sent_cents

            FROM finance_pix_transactions

            WHERE transaction_date BETWEEN ? AND ?
            """,
            (
                start_date,
                end_date,
            ),
        )

        row = cursor.fetchone()

        return dict(row)