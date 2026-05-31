from core.database.database_manager import DatabaseManager


class BalanceRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_ciclo(
            self,
            name: str,
            start_date: str,
            end_date: str,
            opening_balance_source: str = "manual",
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_cycles (
                name,
                start_date,
                end_date,
                opening_balance_source
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                start_date,
                end_date,
                opening_balance_source,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def listar_ciclos_ativos(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                start_date,
                end_date,
                opening_balance_source,
                is_active,
                created_at,
                updated_at
            FROM finance_balance_cycles
            WHERE is_active = 1
            ORDER BY start_date DESC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def criar_receita(
            self,
            cycle_id: int,
            description: str,
            expected_amount_cents: int,
            expected_date: str,
            account_id: int | None = None,
            is_recurring: bool = False,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_income_entries (
                cycle_id,
                account_id,
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
                cycle_id,
                account_id,
                description,
                expected_amount_cents,
                expected_date,
                int(is_recurring),
                notes,
            ),
        )

        self.conexao.commit()
        return cursor.lastrowid

    def listar_receitas_ciclo(
            self,
            cycle_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                cycle_id,
                account_id,
                description,
                expected_amount_cents,
                actual_amount_cents,
                expected_date,
                received_date,
                status,
                is_recurring,
                notes,
                created_at,
                updated_at
            FROM finance_balance_income_entries
            WHERE cycle_id = ?
            ORDER BY expected_date ASC, id ASC
            """,
            (cycle_id,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def criar_compromisso(
            self,
            cycle_id: int,
            description: str,
            expected_amount_cents: int,
            due_date: str,
            payment_type: str = "bank_account",
            account_id: int | None = None,
            credit_card_id: int | None = None,
            is_recurring: bool = False,
            notes: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_balance_commitments (
                cycle_id,
                description,
                expected_amount_cents,
                due_date,
                payment_type,
                account_id,
                credit_card_id,
                status,
                is_recurring,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'expected', ?, ?)
            """,
            (
                cycle_id,
                description,
                expected_amount_cents,
                due_date,
                payment_type,
                account_id,
                credit_card_id,
                int(is_recurring),
                notes,
            ),
        )

        self.conexao.commit()
        return cursor.lastrowid

    def listar_compromissos_ciclo(
            self,
            cycle_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                cycle_id,
                description,
                expected_amount_cents,
                actual_amount_cents,
                due_date,
                paid_date,
                payment_type,
                account_id,
                credit_card_id,
                status,
                is_recurring,
                notes,
                created_at,
                updated_at
            FROM finance_balance_commitments
            WHERE cycle_id = ?
            ORDER BY due_date ASC, id ASC
            """,
            (cycle_id,),
        )

        return [dict(row) for row in cursor.fetchall()]

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

    def buscar_ciclo_por_id(
            self,
            cycle_id: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                start_date,
                end_date,
                opening_balance_source,
                is_active,
                created_at,
                updated_at
            FROM finance_balance_cycles
            WHERE id = ?
            """,
            (cycle_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

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
            is_recurring: bool,
            notes: str | None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_balance_commitments
            SET
                description = ?,
                expected_amount_cents = ?,
                due_date = ?,
                payment_type = ?,
                account_id = ?,
                credit_card_id = ?,
                is_recurring = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                description,
                expected_amount_cents,
                due_date,
                payment_type,
                account_id,
                credit_card_id,
                int(is_recurring),
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

    def obter_resumo_ciclo(
            self,
            cycle_id: int,
    ) -> dict:
        receitas = self.listar_receitas_ciclo(
            cycle_id
        )

        compromissos = self.listar_compromissos_ciclo(
            cycle_id
        )

        receitas_recebidas_cents = 0
        receitas_previstas_cents = 0

        for receita in receitas:
            if receita["status"] == "received":
                receitas_recebidas_cents += (
                        receita["actual_amount_cents"]
                        or 0
                )
            else:
                receitas_previstas_cents += (
                        receita["expected_amount_cents"]
                        or 0
                )

        compromissos_pagos_cents = 0
        compromissos_previstos_cents = 0

        for compromisso in compromissos:
            if compromisso["status"] == "paid":
                compromissos_pagos_cents += (
                        compromisso["actual_amount_cents"]
                        or 0
                )
            else:
                compromissos_previstos_cents += (
                        compromisso["expected_amount_cents"]
                        or 0
                )

        saldo_inicial_cents = 0

        saldo_atual_cents = (
                saldo_inicial_cents
                + receitas_recebidas_cents
                - compromissos_pagos_cents
        )

        saldo_previsto_cents = (
                saldo_atual_cents
                + receitas_previstas_cents
                - compromissos_previstos_cents
        )

        return {
            "cycle_id": cycle_id,
            "saldo_inicial_cents": saldo_inicial_cents,
            "receitas_recebidas_cents": receitas_recebidas_cents,
            "receitas_previstas_cents": receitas_previstas_cents,
            "compromissos_pagos_cents": compromissos_pagos_cents,
            "compromissos_previstos_cents": compromissos_previstos_cents,
            "saldo_atual_cents": saldo_atual_cents,
            "saldo_previsto_cents": saldo_previsto_cents,
        }