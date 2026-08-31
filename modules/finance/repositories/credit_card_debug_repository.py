from core.database.database_manager import DatabaseManager


class CreditCardDebugRepository:
    """
    Acesso CRU aos dados de cartão de crédito.

    Este repository é exclusivo para diagnóstico.

    Regras:
    - não esconder cancelados;
    - não usar INNER JOIN quando isso puder esconder inconsistências;
    - não reconciliar parcelamentos;
    - não reconstruir projeções;
    - não alterar faturas automaticamente;
    - alterações manuais devem ser cirúrgicas.
    """

    def __init__(
            self,
            username: str,
    ) -> None:

        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    # ============================================================
    # CARTÕES
    # ============================================================

    def listar_cartoes(self) -> list[dict]:
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
                cc.is_active,
                cc.created_at,
                cc.updated_at
            FROM finance_credit_cards cc
            ORDER BY
                cc.is_active DESC,
                cc.name ASC,
                cc.id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def buscar_cartao(
            self,
            credit_card_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_cards
            WHERE id = ?
            """,
            (
                credit_card_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # ============================================================
    # FATURAS
    # ============================================================

    def listar_faturas(
            self,
            credit_card_id: int | None = None,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        if credit_card_id is None:
            cursor.execute(
                """
                SELECT
                    i.*,
                    cc.name AS credit_card_name,

                    (
                        SELECT COUNT(*)
                        FROM finance_credit_card_expenses e
                        WHERE e.invoice_id = i.id
                    ) AS raw_expense_count,

                    (
                        SELECT COALESCE(
                            SUM(e.effective_amount_cents),
                            0
                        )
                        FROM finance_credit_card_expenses e
                        WHERE e.invoice_id = i.id
                    ) AS raw_expense_total_cents

                FROM finance_credit_card_invoices i

                LEFT JOIN finance_credit_cards cc
                    ON cc.id = i.credit_card_id

                ORDER BY
                    i.invoice_year DESC,
                    i.invoice_month DESC,
                    i.credit_card_id ASC,
                    i.id ASC
                """
            )

        else:
            cursor.execute(
                """
                SELECT
                    i.*,
                    cc.name AS credit_card_name,

                    (
                        SELECT COUNT(*)
                        FROM finance_credit_card_expenses e
                        WHERE e.invoice_id = i.id
                    ) AS raw_expense_count,

                    (
                        SELECT COALESCE(
                            SUM(e.effective_amount_cents),
                            0
                        )
                        FROM finance_credit_card_expenses e
                        WHERE e.invoice_id = i.id
                    ) AS raw_expense_total_cents

                FROM finance_credit_card_invoices i

                LEFT JOIN finance_credit_cards cc
                    ON cc.id = i.credit_card_id

                WHERE i.credit_card_id = ?

                ORDER BY
                    i.invoice_year DESC,
                    i.invoice_month DESC,
                    i.id ASC
                """,
                (
                    credit_card_id,
                ),
            )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def buscar_fatura(
            self,
            invoice_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                i.*,
                cc.name AS credit_card_name
            FROM finance_credit_card_invoices i

            LEFT JOIN finance_credit_cards cc
                ON cc.id = i.credit_card_id

            WHERE i.id = ?
            """,
            (
                invoice_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # ============================================================
    # LANÇAMENTOS — VERDADE CRUA
    # ============================================================

    def listar_todos_lancamentos(
            self,
            credit_card_id: int | None = None,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        parametros = []
        where = ""

        if credit_card_id is not None:
            where = """
            WHERE e.credit_card_id = ?
            """
            parametros.append(
                credit_card_id
            )

        cursor.execute(
            f"""
            SELECT
                e.*,

                cc.name AS expense_credit_card_name,

                i.id AS joined_invoice_id,
                i.credit_card_id AS invoice_credit_card_id,
                i.invoice_year,
                i.invoice_month,
                i.closing_date AS invoice_closing_date,
                i.due_date AS invoice_due_date,
                i.status AS invoice_status,

                invoice_cc.name AS invoice_credit_card_name,

                b.source_name AS import_source_name,
                b.source_file_name AS import_source_file_name,
                b.created_at AS import_batch_created_at

            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            LEFT JOIN finance_credit_cards invoice_cc
                ON invoice_cc.id = i.credit_card_id

            LEFT JOIN finance_credit_card_import_batches b
                ON b.id = e.import_batch_id

            {where}

            ORDER BY
                e.credit_card_id ASC,
                COALESCE(i.invoice_year, 9999) ASC,
                COALESCE(i.invoice_month, 99) ASC,
                e.installment_group_id ASC,
                e.installment_number ASC,
                e.id ASC
            """,
            parametros,
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def buscar_lancamento(
            self,
            expense_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,

                cc.name AS expense_credit_card_name,

                i.id AS joined_invoice_id,
                i.credit_card_id AS invoice_credit_card_id,
                i.invoice_year,
                i.invoice_month,
                i.closing_date AS invoice_closing_date,
                i.due_date AS invoice_due_date,
                i.status AS invoice_status,

                invoice_cc.name AS invoice_credit_card_name,

                b.source_name AS import_source_name,
                b.source_file_name AS import_source_file_name,
                b.created_at AS import_batch_created_at

            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            LEFT JOIN finance_credit_cards invoice_cc
                ON invoice_cc.id = i.credit_card_id

            LEFT JOIN finance_credit_card_import_batches b
                ON b.id = e.import_batch_id

            WHERE e.id = ?
            """,
            (
                expense_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # ============================================================
    # GRUPOS DE PARCELAMENTO
    # ============================================================

    def listar_grupos(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.installment_group_id,

                COUNT(*) AS total_rows,

                SUM(
                    CASE
                        WHEN e.status = 'cancelled'
                        THEN 1
                        ELSE 0
                    END
                ) AS cancelled_rows,

                SUM(
                    CASE
                        WHEN e.status != 'cancelled'
                        THEN 1
                        ELSE 0
                    END
                ) AS active_rows,

                SUM(
                    CASE
                        WHEN e.source_type = 'projected_installment'
                        THEN 1
                        ELSE 0
                    END
                ) AS projected_rows,

                SUM(
                    CASE
                        WHEN e.source_type != 'projected_installment'
                             OR e.source_type IS NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS real_rows,

                COUNT(
                    DISTINCT e.credit_card_id
                ) AS credit_card_count,

                COUNT(
                    DISTINCT e.installment_total
                ) AS installment_total_variants,

                COUNT(
                    DISTINCT e.installment_number
                ) AS installment_number_count,

                MIN(
                    e.installment_number
                ) AS min_installment_number,

                MAX(
                    e.installment_number
                ) AS max_installment_number,

                MIN(
                    e.effective_purchase_date
                ) AS first_purchase_date,

                MAX(
                    e.effective_purchase_date
                ) AS last_purchase_date,

                MIN(
                    i.invoice_year * 100 + i.invoice_month
                ) AS first_invoice_competence,

                MAX(
                    i.invoice_year * 100 + i.invoice_month
                ) AS last_invoice_competence

            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            WHERE e.installment_group_id IS NOT NULL

            GROUP BY
                e.installment_group_id

            ORDER BY
                e.installment_group_id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_lancamentos_grupo(
            self,
            installment_group_id: str,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,

                cc.name AS expense_credit_card_name,

                i.id AS joined_invoice_id,
                i.credit_card_id AS invoice_credit_card_id,
                i.invoice_year,
                i.invoice_month,
                i.closing_date AS invoice_closing_date,
                i.due_date AS invoice_due_date,
                i.status AS invoice_status,

                invoice_cc.name AS invoice_credit_card_name,

                b.source_name AS import_source_name,
                b.source_file_name AS import_source_file_name

            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            LEFT JOIN finance_credit_cards invoice_cc
                ON invoice_cc.id = i.credit_card_id

            LEFT JOIN finance_credit_card_import_batches b
                ON b.id = e.import_batch_id

            WHERE e.installment_group_id = ?

            ORDER BY
                e.installment_number ASC,
                e.effective_purchase_date ASC,
                e.invoice_id ASC,
                e.id ASC
            """,
            (
                installment_group_id,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # ============================================================
    # FATURA — REGISTROS CRUS
    # ============================================================

    def listar_lancamentos_vinculados_fatura(
            self,
            invoice_id: int,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,

                cc.name AS expense_credit_card_name,

                i.credit_card_id AS invoice_credit_card_id,
                i.invoice_year,
                i.invoice_month,

                invoice_cc.name AS invoice_credit_card_name

            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            LEFT JOIN finance_credit_cards invoice_cc
                ON invoice_cc.id = i.credit_card_id

            WHERE e.invoice_id = ?

            ORDER BY
                e.status ASC,
                e.installment_group_id ASC,
                e.installment_number ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            (
                invoice_id,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # ============================================================
    # AJUSTES
    # ============================================================

    def listar_ajustes_fatura_raw(
            self,
            invoice_id: int,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                a.*,

                i.credit_card_id AS invoice_credit_card_id,
                i.invoice_year,
                i.invoice_month,

                cc.name AS adjustment_credit_card_name,
                invoice_cc.name AS invoice_credit_card_name

            FROM finance_credit_card_invoice_adjustments a

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = a.invoice_id

            LEFT JOIN finance_credit_cards cc
                ON cc.id = a.credit_card_id

            LEFT JOIN finance_credit_cards invoice_cc
                ON invoice_cc.id = i.credit_card_id

            WHERE a.invoice_id = ?

            ORDER BY
                a.adjustment_date ASC,
                a.id ASC
            """,
            (
                invoice_id,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # ============================================================
    # REGISTROS POTENCIALMENTE ÓRFÃOS
    # ============================================================

    def listar_lancamentos_sem_fatura(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,
                cc.name AS credit_card_name
            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            WHERE e.invoice_id IS NULL

            ORDER BY
                e.credit_card_id ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_lancamentos_com_fatura_inexistente(
            self,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,
                cc.name AS credit_card_name
            FROM finance_credit_card_expenses e

            LEFT JOIN finance_credit_cards cc
                ON cc.id = e.credit_card_id

            LEFT JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            WHERE e.invoice_id IS NOT NULL
              AND i.id IS NULL

            ORDER BY
                e.credit_card_id ASC,
                e.invoice_id ASC,
                e.id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_lancamentos_cartao_fatura_divergentes(
            self,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,

                cc_expense.name AS expense_credit_card_name,

                i.credit_card_id AS invoice_credit_card_id,
                i.invoice_year,
                i.invoice_month,

                cc_invoice.name AS invoice_credit_card_name

            FROM finance_credit_card_expenses e

            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id

            LEFT JOIN finance_credit_cards cc_expense
                ON cc_expense.id = e.credit_card_id

            LEFT JOIN finance_credit_cards cc_invoice
                ON cc_invoice.id = i.credit_card_id

            WHERE e.credit_card_id != i.credit_card_id

            ORDER BY
                e.id ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # ============================================================
    # DUPLICIDADES / COLISÕES
    # ============================================================

    def listar_parcelas_duplicadas_no_grupo(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                installment_group_id,
                installment_number,

                COUNT(*) AS total_rows,

                SUM(
                    CASE
                        WHEN status != 'cancelled'
                        THEN 1
                        ELSE 0
                    END
                ) AS active_rows,

                GROUP_CONCAT(
                    id
                ) AS expense_ids,

                GROUP_CONCAT(
                    status
                ) AS statuses,

                GROUP_CONCAT(
                    COALESCE(source_type, 'NULL')
                ) AS source_types

            FROM finance_credit_card_expenses

            WHERE installment_group_id IS NOT NULL

            GROUP BY
                installment_group_id,
                installment_number

            HAVING SUM(
                CASE
                    WHEN status != 'cancelled'
                    THEN 1
                    ELSE 0
                END
            ) > 1

            ORDER BY
                installment_group_id ASC,
                installment_number ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_colisoes_real_projecao(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                installment_group_id,
                installment_number,

                COUNT(*) AS total_rows,

                SUM(
                    CASE
                        WHEN source_type = 'projected_installment'
                             AND status != 'cancelled'
                        THEN 1
                        ELSE 0
                    END
                ) AS projected_active_rows,

                SUM(
                    CASE
                        WHEN (
                            source_type != 'projected_installment'
                            OR source_type IS NULL
                        )
                        AND status != 'cancelled'
                        THEN 1
                        ELSE 0
                    END
                ) AS real_active_rows,

                GROUP_CONCAT(
                    id
                ) AS expense_ids

            FROM finance_credit_card_expenses

            WHERE installment_group_id IS NOT NULL

            GROUP BY
                installment_group_id,
                installment_number

            HAVING projected_active_rows > 0
               AND real_active_rows > 0

            ORDER BY
                installment_group_id ASC,
                installment_number ASC
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # ============================================================
    # INTEGRIDADE SQLITE
    # ============================================================

    def executar_foreign_key_check(self) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            PRAGMA foreign_key_check
            """
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    # ============================================================
    # ALTERAÇÕES CIRÚRGICAS
    # ============================================================

    def alterar_installment_group_id(
            self,
            expense_id: int,
            installment_group_id: str | None,
    ) -> None:
        """
        Altera SOMENTE installment_group_id.

        Não reconcilia.
        Não altera outras parcelas.
        Não altera invoice_id.
        Não altera datas.
        Não altera valores.
        """

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                installment_group_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                installment_group_id,
                expense_id,
            ),
        )

        if cursor.rowcount != 1:
            self.conexao.rollback()

            raise ValueError(
                f"Lançamento não encontrado: {expense_id}"
            )

        self.conexao.commit()

    def alterar_invoice_id(
            self,
            expense_id: int,
            invoice_id: int | None,
    ) -> None:
        """
        Ferramenta de baixo nível para diagnóstico.

        Altera SOMENTE invoice_id.

        O service deverá exigir confirmação explícita antes
        de expor essa operação na interface.
        """

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                invoice_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                invoice_id,
                expense_id,
            ),
        )

        if cursor.rowcount != 1:
            self.conexao.rollback()

            raise ValueError(
                f"Lançamento não encontrado: {expense_id}"
            )

        self.conexao.commit()

    def alterar_status_lancamento(
            self,
            expense_id: int,
            status: str,
    ) -> None:
        """
        Altera SOMENTE o status.

        Será usado posteriormente pelo debugger para
        cancelamento/restauração explícitos.
        """

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                status,
                expense_id,
            ),
        )

        if cursor.rowcount != 1:
            self.conexao.rollback()

            raise ValueError(
                f"Lançamento não encontrado: {expense_id}"
            )

        self.conexao.commit()