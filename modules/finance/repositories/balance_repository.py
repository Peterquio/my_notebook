from core.database.database_manager import DatabaseManager


class BalanceRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_receita(
            self,
            description: str,
            expected_amount_cents: int,
            expected_date: str,
            account_id: int | None = None,
            is_recurring: bool = False,
            notes: str | None = None,
            external_reference: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_income_entries (
                account_id,
                external_reference,
                description,
                expected_amount_cents,
                expected_date,
                status,
                is_recurring,
                notes
            )
            VALUES (?, ?, ?, ?, ?, 'expected', ?, ?)
            """,
            (
                account_id,
                external_reference,
                description,
                expected_amount_cents,
                expected_date,
                int(is_recurring),
                notes,
            ),
        )

        self.conexao.commit()
        return cursor.lastrowid

    def criar_compromisso(
            self,
            description: str,
            expected_amount_cents: int,
            due_date: str,
            payment_type: str = "bank_account",
            account_id: int | None = None,
            credit_card_id: int | None = None,
            is_recurring: bool = False,
            notes: str | None = None,
            external_reference: str | None = None,
            status: str = "expected",
            commitment_origin: str = "manual",
            projection_type: str = "real",
            actual_amount_cents: int | None = None,
            paid_date: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_commitments (
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                status,
                commitment_origin,
                projection_type,
                is_recurring,
                external_reference,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                status,
                commitment_origin,
                projection_type,
                int(is_recurring),
                external_reference,
                notes,
            ),
        )

        self.conexao.commit()
        return cursor.lastrowid

    def confirmar_receita(
            self,
            receita_id: int,
            valor_real_cents: int,
            received_date: str,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_income_entries
            SET
                status = 'received',
                actual_amount_cents = ?,
                received_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                valor_real_cents,
                received_date,
                receita_id,
            ),
        )

        self.conexao.commit()

    def reabrir_receita(
            self,
            receita_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_income_entries
            SET
                status = 'expected',
                actual_amount_cents = NULL,
                received_date = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (receita_id,),
        )

        self.conexao.commit()

    def confirmar_compromisso(
            self,
            compromisso_id: int,
            valor_real_cents: int,
            paid_date: str,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_commitments
            SET
                status = 'paid',
                actual_amount_cents = ?,
                paid_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                valor_real_cents,
                paid_date,
                compromisso_id,
            ),
        )

        self.conexao.commit()

    def reabrir_compromisso(
            self,
            compromisso_id: int,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_commitments
            SET
                status = 'expected',
                actual_amount_cents = NULL,
                paid_date = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (compromisso_id,),
        )

        self.conexao.commit()

    def atualizar_receita(
            self,
            receita_id: int,
            account_id: int,
            description: str,
            expected_amount_cents: int,
            expected_date: str,
            is_recurring: bool,
            notes: str | None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_income_entries
            SET
                account_id = ?,
                description = ?,
                expected_amount_cents = ?,
                expected_date = ?,
                is_recurring = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                account_id,
                description,
                expected_amount_cents,
                expected_date,
                int(is_recurring),
                notes,
                receita_id,
            ),
        )

        self.conexao.commit()

    def excluir_receita(
            self,
            receita_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_balance_income_entries
            WHERE id = ?
            """,
            (receita_id,),
        )

        self.conexao.commit()

    def atualizar_compromisso(
            self,
            compromisso_id: int,
            description: str,
            expected_amount_cents: int,
            due_date: str,
            payment_type: str,
            account_id: int | None,
            credit_card_id: int | None,
            is_recurring: bool = False,
            notes: str | None = None,
            external_reference: str | None = None,
            status: str = "expected",
            commitment_origin: str = "manual",
            projection_type: str = "real",
            actual_amount_cents: int | None = None,
            paid_date: str | None = None,
    ) -> None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_commitments
            SET
                description = ?,
                expected_amount_cents = ?,
                actual_amount_cents = ?,
                due_date = ?,
                paid_date = ?,
                payment_type = ?,
                account_id = ?,
                credit_card_id = ?,
                status = ?,
                commitment_origin = ?,
                projection_type = ?,
                is_recurring = ?,
                external_reference = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                status,
                commitment_origin,
                projection_type,
                int(is_recurring),
                external_reference,
                notes,
                compromisso_id,
            ),
        )

        self.conexao.commit()

    def excluir_compromisso(
            self,
            compromisso_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            DELETE FROM finance_balance_commitments
            WHERE id = ?
            """,
            (compromisso_id,),
        )

        self.conexao.commit()

    def listar_compromissos_por_prefixo_external_reference(
            self,
            prefixo_external_reference: str,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_commitments
            WHERE external_reference LIKE ?
            ORDER BY id ASC
            """,
            (
                f"{prefixo_external_reference}%",
            ),
        )

        return [dict(row) for row in cursor.fetchall()]

    def buscar_compromisso_cartao(
            self,
            credit_card_id: int,
            due_date: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                status,
                commitment_origin,
                projection_type,
                is_recurring,
                notes,
                created_at,
                updated_at
            FROM finance_balance_commitments
            WHERE credit_card_id = ?
              AND due_date = ?
              AND payment_type = 'credit_card'
            LIMIT 1
            """,
            (
                credit_card_id,
                due_date,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def sincronizar_compromisso_cartao(
            self,
            credit_card_id: int,
            account_id: int | None,
            description: str,
            expected_amount_cents: int,
            due_date: str,
            notes: str | None = None,
            commitment_origin: str = "credit_card_open",
            projection_type: str = "real",
    ) -> int:
        compromisso = self.buscar_compromisso_cartao(
            credit_card_id=credit_card_id,
            due_date=due_date,
        )

        if compromisso is None:
            return self.criar_compromisso(
                description=description,
                expected_amount_cents=expected_amount_cents,
                due_date=due_date,
                payment_type="credit_card",
                account_id=account_id,
                credit_card_id=credit_card_id,
                is_recurring=False,
                commitment_origin=commitment_origin,
                projection_type=projection_type,
                notes=notes,
            )

        if compromisso["status"] == "paid":
            return compromisso["id"]

        self.atualizar_compromisso(
            compromisso_id=compromisso["id"],
            description=description,
            expected_amount_cents=expected_amount_cents,
            due_date=due_date,
            payment_type="credit_card",
            account_id=account_id,
            credit_card_id=credit_card_id,
            is_recurring=False,
            commitment_origin=commitment_origin,
            projection_type=projection_type,
            notes=notes,
        )

        return compromisso["id"]

    def buscar_compromisso_por_external_reference(
            self,
            external_reference: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_commitments
            WHERE external_reference = ?
            LIMIT 1
            """,
            (
                external_reference,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def buscar_receita_por_external_reference(
            self,
            external_reference: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_income_entries
            WHERE external_reference = ?
            LIMIT 1
            """,
            (
                external_reference,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def upsert_compromisso_por_external_reference(
            self,
            external_reference: str,
            **dados,
    ) -> int:

        compromisso = (
            self.buscar_compromisso_por_external_reference(
                external_reference
            )
        )

        if compromisso is None:
            return self.criar_compromisso(
                external_reference=external_reference,
                **dados,
            )

        if compromisso["status"] == "paid":
            return compromisso["id"]

        self.atualizar_compromisso(
            compromisso_id=compromisso["id"],
            external_reference=external_reference,
            **dados,
        )

        return compromisso["id"]

    def atualizar_conta_compromissos_cartao_sincronizados(
            self,
            credit_card_id: int,
            account_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        prefixo = f"cc:{credit_card_id}:%"

        cursor.execute(
            """
            UPDATE finance_balance_commitments
            SET
                account_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE credit_card_id = ?
              AND payment_type = 'credit_card'
              AND external_reference LIKE ?
              AND status != 'paid'
            """,
            (
                account_id,
                credit_card_id,
                prefixo,
            ),
        )

        self.conexao.commit()

    def listar_receitas_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_income_entries
            WHERE expected_date BETWEEN ? AND ?
            ORDER BY expected_date ASC, id ASC
            """,
            (
                start_date,
                end_date,
            ),
        )

        return [dict(row) for row in cursor.fetchall()]

    def listar_compromissos_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_balance_commitments
            WHERE
                CASE
                    WHEN status = 'paid'
                         AND paid_date IS NOT NULL
                    THEN paid_date
                    ELSE due_date
                END BETWEEN ? AND ?
            ORDER BY
                CASE
                    WHEN status = 'paid'
                         AND paid_date IS NOT NULL
                    THEN paid_date
                    ELSE due_date
                END ASC,
                id ASC
            """,
            (
                start_date,
                end_date,
            ),
        )

        return [dict(row) for row in cursor.fetchall()]

        return [dict(row) for row in cursor.fetchall()]