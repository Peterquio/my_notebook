from core.database.database_manager import DatabaseManager


class CreditCardExpenseRepository:
    def __init__(self, username: str) -> None:
        self.database = DatabaseManager(username)
        self.conexao = self.database.get_connection()

    def criar_lancamento(
            self,
            credit_card_id: int,
            invoice_id: int,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            billing_date: str,
            installment_number: int,
            installment_total: int,
            effective_amount_cents: int,
            subcategory: str | None = None,
            installment_group_id: str | None = None,
            notes: str | None = None,
            original_description: str | None = None,
            original_purchase_date: str | None = None,
            original_amount_cents: int | None = None,
            source_type: str | None = None,
            source_reference: str | None = None,
            import_batch_id: int | None = None,
            created_by: str | None = None,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO finance_credit_card_expenses (
                credit_card_id,
                invoice_id,
                category_id,

                original_description,
                effective_description,

                original_purchase_date,
                effective_purchase_date,

                original_amount_cents,
                effective_amount_cents,
                
                subcategory,

                billing_date,

                installment_number,
                installment_total,

                installment_group_id,

                source_type,
                source_reference,

                import_batch_id,
                created_by,

                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                credit_card_id,
                invoice_id,
                category_id,

                original_description,
                effective_description,

                original_purchase_date,
                effective_purchase_date,

                original_amount_cents,
                effective_amount_cents,

                subcategory,

                billing_date,

                installment_number,
                installment_total,

                installment_group_id,

                source_type,
                source_reference,

                import_batch_id,
                created_by,

                notes,
            ),
        )

        self.conexao.commit()

        return cursor.lastrowid

    def atualizar_categoria(
            self,
            expense_id: int,
            category_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                category_id = ?
            WHERE id = ?
            """,
            (
                category_id,
                expense_id,
            ),
        )

        self.conexao.commit()

    def somar_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(e.effective_amount_cents), 0) AS total_cents
            FROM finance_credit_card_expenses e
                     INNER JOIN finance_credit_card_invoices i
                                ON i.id = e.invoice_id
            WHERE e.credit_card_id = ?
              AND i.invoice_year = ?
              AND i.invoice_month = ?
              AND e.status != 'cancelled'
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
            ),
        )

        row = cursor.fetchone()

        return int(row["total_cents"])

    def somar_faturas_futuras(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(e.effective_amount_cents), 0) AS total_cents
            FROM finance_credit_card_expenses e
            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id
            WHERE e.credit_card_id = ?
              AND (
                    i.invoice_year > ?
                    OR (
                        i.invoice_year = ?
                        AND i.invoice_month > ?
                    )
              )
              AND e.status != 'cancelled'
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_year,
                invoice_month,
            ),
        )

        row = cursor.fetchone()

        return int(row["total_cents"] or 0)

    def listar_lancamentos_por_fatura(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
            sort_mode: str = "categoria",
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        order_by_options = {
            "data": """
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "categoria": """
                c.display_number ASC,
                e.installment_number ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "alfabetica": """
                e.effective_description ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "valor": """
                e.effective_amount_cents DESC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            "parcelas": """
                CASE
                    WHEN e.installment_total > 1 THEN 0
                    ELSE 1
                END ASC,
                e.installment_number DESC,
                e.installment_total DESC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
        }

        order_by = order_by_options.get(
            sort_mode,
            order_by_options["categoria"],
        )

        cursor.execute(
            """
            SELECT
                e.id AS expense_id,
                e.credit_card_id,
                e.invoice_id,
                e.category_id,

                e.effective_description,
                e.effective_purchase_date,
                e.effective_amount_cents,
                
                e.subcategory,
                e.notes,

                e.original_description,
                e.original_purchase_date,
                e.original_amount_cents,

                e.billing_date,
                e.installment_number,
                e.installment_total,
                e.installment_group_id,
                e.source_type,
                e.source_reference,
                e.status,

                c.name AS category_name,
                c.color AS category_color,

                i.invoice_year,
                i.invoice_month
            FROM finance_credit_card_expenses e
            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id
            LEFT JOIN finance_categories c
                ON c.id = e.category_id
            WHERE e.credit_card_id = ?
              AND i.invoice_year = ?
              AND i.invoice_month = ?
              AND e.status != 'cancelled'
            ORDER BY
            """ + order_by,
            (
                credit_card_id,
                invoice_year,
                invoice_month,
            ),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def listar_por_cartao(
            self,
            credit_card_id: int,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
            ORDER BY effective_purchase_date
            """,
            (credit_card_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def atualizar_invoice_id(
            self,
            expense_id: int,
            invoice_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET invoice_id = ?
            WHERE id = ?
            """,
            (
                invoice_id,
                expense_id,
            ),
        )

        self.conexao.commit()

    def existe_lancamento_importado(
            self,
            credit_card_id: int,
            original_description: str,
            original_purchase_date: str,
            original_amount_cents: int,
            installment_number: int,
            installment_total: int,
    ) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND original_description = ?
              AND original_purchase_date = ?
              AND original_amount_cents = ?
              AND installment_number = ?
              AND installment_total = ?
              AND status != 'cancelled'
            LIMIT 1
            """,
            (
                credit_card_id,
                original_description,
                original_purchase_date,
                original_amount_cents,
                installment_number,
                installment_total,
            ),
        )

        return cursor.fetchone() is not None

    def contar_lancamentos_por_assinatura(
            self,
            credit_card_id: int,
            original_description: str,
            original_purchase_date: str,
            original_amount_cents: int,
            installment_number: int,
            installment_total: int,
    ) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND original_description = ?
              AND original_purchase_date = ?
              AND original_amount_cents = ?
              AND installment_number = ?
              AND installment_total = ?
              AND status != 'cancelled'
            """,
            (
                credit_card_id,
                original_description,
                original_purchase_date,
                original_amount_cents,
                installment_number,
                installment_total,
            ),
        )

        row = cursor.fetchone()

        return int(row["total"] or 0)

    def atualizar_lancamento(
            self,
            expense_id: int,
            invoice_id: int,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            billing_date: str,
            effective_amount_cents: int,
            subcategory: str | None = None,
            notes: str | None = None,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                invoice_id = ?,
                category_id = ?,
                effective_description = ?,
                effective_purchase_date = ?,
                billing_date = ?,
                effective_amount_cents = ?,
                subcategory = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status != 'cancelled'
            """,
            (
                invoice_id,
                category_id,
                effective_description,
                effective_purchase_date,
                billing_date,
                effective_amount_cents,
                subcategory,
                notes,
                expense_id,
            ),
        )

        self.conexao.commit()

    def buscar_installment_group_id_compativel(
            self,
            credit_card_id: int,
            descricao_normalizada: str,
            effective_amount_cents: int,
            installment_number: int,
            installment_total: int,
            competencia_primeira: str,
            tolerancia_centavos: int = 50,
    ) -> str | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT DISTINCT installment_group_id
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND installment_group_id IS NOT NULL
              AND installment_total = ?
              AND status != 'cancelled'
            ORDER BY id ASC
            """,
            (
                credit_card_id,
                installment_total,
            ),
        )

        candidatos_exatos = []
        candidatos_fallback = []

        for row in cursor.fetchall():
            installment_group_id = row["installment_group_id"]

            base_group_id = installment_group_id.split(
                "|occurrence:",
                1,
            )[0]

            partes = base_group_id.split("|")

            if len(partes) < 5:
                continue

            try:
                grupo_credit_card_id = int(partes[0])
                grupo_amount_cents = int(partes[-3])
                grupo_installment_total = int(partes[-2])
            except ValueError:
                continue

            grupo_descricao = "|".join(partes[1:-3])
            grupo_competencia_primeira = partes[-1]

            if grupo_credit_card_id != credit_card_id:
                continue

            if grupo_installment_total != installment_total:
                continue

            if grupo_competencia_primeira != competencia_primeira:
                continue

            diferenca = abs(
                grupo_amount_cents - effective_amount_cents
            )

            if diferenca > tolerancia_centavos:
                continue

            cursor_verificacao = self.conexao.cursor()

            cursor_verificacao.execute(
                """
                SELECT 1
                FROM finance_credit_card_expenses
                WHERE credit_card_id = ?
                  AND installment_group_id = ?
                  AND installment_number = ?
                  AND source_type != 'projected_installment'
                  AND status != 'cancelled'
                LIMIT 1
                """,
                (
                    credit_card_id,
                    installment_group_id,
                    installment_number,
                ),
            )

            # Já existe uma parcela REAL desse número nesse grupo.
            # Portanto esta importação não pode pertencer a ele.
            if cursor_verificacao.fetchone() is not None:
                continue

            candidato = (
                diferenca,
                installment_group_id,
            )

            if grupo_descricao == descricao_normalizada:
                candidatos_exatos.append(candidato)
            else:
                candidatos_fallback.append(candidato)

        # 1. Sempre prioriza descrição exata.
        if candidatos_exatos:
            candidatos_exatos.sort(
                key=lambda item: item[0]
            )

            return candidatos_exatos[0][1]

        # 2. Sem descrição exata, somente aceita fallback
        #    quando há UM ÚNICO grupo possível.
        if len(candidatos_fallback) == 1:
            return candidatos_fallback[0][1]

        # Ambíguo: é melhor criar outro grupo do que
        # misturar dois parcelamentos diferentes.
        return None

    def listar_grupos_parcelados(
            self,
            credit_card_id: int,
    ) -> list[str]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT DISTINCT installment_group_id
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND installment_group_id IS NOT NULL
              AND status != 'cancelled'
            ORDER BY installment_group_id
            """,
            (credit_card_id,),
        )

        return [
            row["installment_group_id"]
            for row in cursor.fetchall()
        ]

    def listar_parcelas_grupo(
            self,
            installment_group_id: str,
    ) -> list[dict]:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT
                e.*,
                i.invoice_year,
                i.invoice_month
            FROM finance_credit_card_expenses e
            INNER JOIN finance_credit_card_invoices i
                ON i.id = e.invoice_id
            WHERE e.installment_group_id = ?
              AND e.status != 'cancelled'
            ORDER BY
                e.installment_number ASC,
                e.effective_purchase_date ASC,
                e.id ASC
            """,
            (installment_group_id,),
        )

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    def buscar_parcela_real_referencia_grupo(
            self,
            installment_group_id: str,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_expenses
            WHERE installment_group_id = ?
              AND source_type != 'projected_installment'
              AND status != 'cancelled'
            ORDER BY
                installment_number DESC,
                id DESC
            LIMIT 1
            """,
            (installment_group_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def buscar_parcela_grupo(
            self,
            installment_group_id: str,
            installment_number: int,
    ) -> dict | None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_expenses
            WHERE installment_group_id = ?
              AND installment_number = ?
              AND status != 'cancelled'
            ORDER BY id ASC
            LIMIT 1
            """,
            (
                installment_group_id,
                installment_number,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def buscar_por_id(
            self,
            expense_id: int,
    ) -> dict | None:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_expenses
            WHERE id = ?
              AND status != 'cancelled'
            """,
            (expense_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    def atualizar_parcela(
            self,
            expense_id: int,
            invoice_id: int,
            effective_purchase_date: str,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                invoice_id = ?,
                effective_purchase_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                invoice_id,
                effective_purchase_date,
                expense_id,
            ),
        )

        self.conexao.commit()

    def cancelar_projecoes_parcelamento_cartao(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE id IN (
                SELECT e.id
                FROM finance_credit_card_expenses e
                INNER JOIN finance_credit_card_invoices i
                    ON i.id = e.invoice_id
                WHERE e.credit_card_id = ?
                  AND e.source_type = 'projected_installment'
                  AND e.status != 'cancelled'
                  AND (
                        i.invoice_year > ?
                        OR (
                            i.invoice_year = ?
                            AND i.invoice_month >= ?
                        )
                  )
            )
            """,
            (
                credit_card_id,
                invoice_year,
                invoice_year,
                invoice_month,
            ),
        )

        self.conexao.commit()

    def fatura_possui_importacao_csv(
            self,
            credit_card_id: int,
            invoice_id: int,
    ) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND invoice_id = ?
              AND created_by = 'csv_import'
              AND status != 'cancelled'
            LIMIT 1
            """,
            (
                credit_card_id,
                invoice_id,
            ),
        )

        return cursor.fetchone() is not None

    def listar_lancamentos_match_assinatura(
            self,
            credit_card_id: int,
            start_date: str,
            end_date: str,
            amount_cents: int,
            tolerancia_centavos: int = 50,
    ) -> list[dict]:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT *
            FROM finance_credit_card_expenses
            WHERE credit_card_id = ?
              AND effective_purchase_date BETWEEN ? AND ?
              AND ABS(effective_amount_cents - ?) <= ?
              AND status != 'cancelled'
            ORDER BY effective_purchase_date ASC, id ASC
            """,
            (
                credit_card_id,
                start_date,
                end_date,
                amount_cents,
                tolerancia_centavos,
            ),
        )

        return [dict(row) for row in cursor.fetchall()]

    def cancelar_lancamento(
            self,
            expense_id: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status != 'cancelled'
            """,
            (expense_id,),
        )

        self.conexao.commit()

    def cancelar_parcelamento_inteiro(
            self,
            installment_group_id: str,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE installment_group_id = ?
              AND status != 'cancelled'
            """,
            (installment_group_id,),
        )

        self.conexao.commit()

    def cancelar_parcelas_a_partir_de(
            self,
            installment_group_id: str,
            installment_number: int,
            invoice_year: int,
            invoice_month: int,
    ) -> None:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE finance_credit_card_expenses
            SET
                status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE id IN (
                SELECT e.id
                FROM finance_credit_card_expenses e
                INNER JOIN finance_credit_card_invoices i
                    ON i.id = e.invoice_id
                WHERE e.installment_group_id = ?
                  AND e.installment_number >= ?
                  AND e.status != 'cancelled'
                  AND (
                        i.invoice_year > ?
                        OR (
                            i.invoice_year = ?
                            AND i.invoice_month >= ?
                        )
                  )
            )
            """,
            (
                installment_group_id,
                installment_number,
                invoice_year,
                invoice_year,
                invoice_month,
            ),
        )

        self.conexao.commit()