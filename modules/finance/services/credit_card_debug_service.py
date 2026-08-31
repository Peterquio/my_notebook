from __future__ import annotations

from datetime import date, datetime
from typing import Any

from modules.finance.repositories.credit_card_debug_repository import (
    CreditCardDebugRepository,
)

from modules.finance.services.credit_card_debug_logger import (
    CreditCardDebugLogger,
)

from modules.finance.services.credit_card_detail_service import (
    CreditCardDetailService,
)


class CreditCardDebugService:
    """
    Serviço de diagnóstico de cartões de crédito.

    IMPORTANTE:
    - não reconcilia automaticamente;
    - não cria projeções;
    - não recalcula grupos;
    - não modifica meses anteriores;
    - diagnóstico é separado de correção;
    - alterações manuais são cirúrgicas e logadas.
    """

    def __init__(
            self,
            username: str,
            logger: CreditCardDebugLogger | None = None,
    ) -> None:

        self.username = username

        self.repository = CreditCardDebugRepository(
            username
        )

        self.detail_service = CreditCardDetailService(
            username
        )

        self.logger = (
            logger
            if logger is not None
            else CreditCardDebugLogger()
        )

    # ============================================================
    # ACESSO BÁSICO
    # ============================================================

    def listar_cartoes(self) -> list[dict]:
        return self.repository.listar_cartoes()

    def listar_faturas(
            self,
            credit_card_id: int | None = None,
    ) -> list[dict]:

        return self.repository.listar_faturas(
            credit_card_id=credit_card_id,
        )

    def listar_grupos(self) -> list[dict]:
        return self.repository.listar_grupos()

    def listar_lancamentos_grupo(
            self,
            installment_group_id: str,
    ) -> list[dict]:

        return self.repository.listar_lancamentos_grupo(
            installment_group_id
        )

    def obter_log(self) -> str:
        return self.logger.obter_texto()

    def limpar_log(self) -> None:
        self.logger.limpar()

    # ============================================================
    # CLASSIFICAÇÃO DE UM LANÇAMENTO
    # ============================================================

    def classificar_lancamento(
            self,
            lancamento: dict,
    ) -> dict:

        problemas = []
        warnings = []

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        if lancamento.get("status") == "cancelled":
            problemas.append(
                "CANCELLED"
            )

        # --------------------------------------------------------
        # FATURA
        # --------------------------------------------------------

        invoice_id = lancamento.get(
            "invoice_id"
        )

        joined_invoice_id = lancamento.get(
            "joined_invoice_id"
        )

        if invoice_id is None:
            problemas.append(
                "NO_INVOICE"
            )

        elif joined_invoice_id is None:
            problemas.append(
                "ORPHAN_INVOICE"
            )

        # --------------------------------------------------------
        # CARTÃO DO LANÇAMENTO X CARTÃO DA FATURA
        # --------------------------------------------------------

        expense_credit_card_id = lancamento.get(
            "credit_card_id"
        )

        invoice_credit_card_id = lancamento.get(
            "invoice_credit_card_id"
        )

        if (
                joined_invoice_id is not None
                and expense_credit_card_id is not None
                and invoice_credit_card_id is not None
                and expense_credit_card_id
                != invoice_credit_card_id
        ):
            problemas.append(
                "CARD_INVOICE_MISMATCH"
            )

        # --------------------------------------------------------
        # FATURA ESPERADA PELA DATA
        # --------------------------------------------------------

        expected = self._calcular_competencia_esperada(
            lancamento
        )

        actual = self._obter_competencia_atual(
            lancamento
        )

        if (
                expected is not None
                and actual is not None
                and expected != actual
        ):
            warnings.append(
                "ASSIGNED_VS_EXPECTED_INVOICE"
            )

        return {
            "expense_id": lancamento.get("id"),
            "problems": problemas,
            "warnings": warnings,
            "expected_invoice": expected,
            "actual_invoice": actual,
        }

    # ============================================================
    # AUDITORIA DE FATURA
    # ============================================================

    def auditar_fatura(
            self,
            invoice_id: int,
    ) -> dict:

        fatura = self.repository.buscar_fatura(
            invoice_id
        )

        if fatura is None:
            raise ValueError(
                f"Fatura não encontrada: {invoice_id}"
            )

        credit_card_id = fatura[
            "credit_card_id"
        ]

        invoice_year = fatura[
            "invoice_year"
        ]

        invoice_month = fatura[
            "invoice_month"
        ]

        cartao = self.repository.buscar_cartao(
            credit_card_id
        )

        if cartao is None:
            raise ValueError(
                f"Cartão da fatura não encontrado: "
                f"{credit_card_id}"
            )

        identificador = (
            f"invoice_id={invoice_id} | "
            f"card={credit_card_id} | "
            f"{invoice_month:02d}/{invoice_year}"
        )

        self.logger.inicio_auditoria(
            tipo="FATURA",
            identificador=identificador,
        )

        # ========================================================
        # VERDADE CRUA DO BANCO
        # ========================================================

        raw_rows = (
            self.repository
            .listar_lancamentos_vinculados_fatura(
                invoice_id
            )
        )

        raw_total_cents = sum(
            int(
                row.get(
                    "effective_amount_cents"
                )
                or 0
            )
            for row in raw_rows
        )

        # ========================================================
        # VERDADE DO CÁLCULO REAL
        #
        # Usa o MESMO repository que o app normal.
        # ========================================================

        calculation_rows = (
            self.detail_service
            .expense_repository
            .listar_lancamentos_por_fatura(
                credit_card_id=credit_card_id,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
                sort_mode="parcelas",
            )
        )

        calculation_ids = {
            row["id"]
            for row in calculation_rows
        }

        calculation_total_cents = sum(
            int(
                row.get(
                    "effective_amount_cents"
                )
                or 0
            )
            for row in calculation_rows
        )

        # ========================================================
        # RESULTADO OFICIAL DO SERVICE
        # ========================================================

        official = (
            self.detail_service
            .carregar_fatura_por_mes(
                credit_card=cartao,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
                sort_mode="parcelas",
            )
        )

        # ========================================================
        # AJUSTES CRUDOS
        # ========================================================

        raw_adjustments = (
            self.repository
            .listar_ajustes_fatura_raw(
                invoice_id
            )
        )

        # ========================================================
        # CLASSIFICAR LINHAS
        # ========================================================

        rows = []

        problemas_encontrados = 0

        for raw in raw_rows:
            classificacao = (
                self.classificar_lancamento(
                    raw
                )
            )

            used = (
                raw["id"]
                in calculation_ids
            )

            motivos = list(
                classificacao["problems"]
            )

            warnings = list(
                classificacao["warnings"]
            )

            if not used:
                if raw.get("status") == "cancelled":
                    motivo_calculo = (
                        "EXCLUDED_CANCELLED"
                    )

                elif raw.get("invoice_id") is None:
                    motivo_calculo = (
                        "EXCLUDED_NO_INVOICE"
                    )

                elif raw.get(
                        "joined_invoice_id"
                ) is None:
                    motivo_calculo = (
                        "EXCLUDED_ORPHAN_INVOICE"
                    )

                elif (
                        raw.get("credit_card_id")
                        != raw.get(
                            "invoice_credit_card_id"
                        )
                ):
                    motivo_calculo = (
                        "EXCLUDED_CARD_MISMATCH"
                    )

                else:
                    motivo_calculo = (
                        "NOT_USED_UNEXPLAINED"
                    )

                    motivos.append(
                        "NOT_USED_UNEXPLAINED"
                    )

            else:
                motivo_calculo = "USED"

            if motivos or warnings:
                problemas_encontrados += 1

            rows.append(
                {
                    **raw,

                    "used_in_calculation": used,

                    "calculation_status": (
                        motivo_calculo
                    ),

                    "debug_problems": motivos,

                    "debug_warnings": warnings,

                    "expected_invoice": (
                        classificacao[
                            "expected_invoice"
                        ]
                    ),

                    "actual_invoice": (
                        classificacao[
                            "actual_invoice"
                        ]
                    ),
                }
            )

        # ========================================================
        # DIVERGÊNCIAS DE TOTAIS
        # ========================================================

        excluded_rows = [
            row
            for row in rows
            if not row[
                "used_in_calculation"
            ]
        ]

        excluded_total_cents = sum(
            int(
                row.get(
                    "effective_amount_cents"
                )
                or 0
            )
            for row in excluded_rows
        )

        expected_difference_cents = (
            raw_total_cents
            - calculation_total_cents
        )

        # ========================================================
        # LOG
        # ========================================================

        resumo = {
            "invoice_id": invoice_id,
            "credit_card_id": credit_card_id,

            "competence": (
                f"{invoice_month:02d}/"
                f"{invoice_year}"
            ),

            "raw_rows": len(
                raw_rows
            ),

            "raw_total_cents": (
                raw_total_cents
            ),

            "calculation_rows": len(
                calculation_rows
            ),

            "calculation_total_cents": (
                calculation_total_cents
            ),

            "excluded_rows": len(
                excluded_rows
            ),

            "excluded_total_cents": (
                excluded_total_cents
            ),

            "raw_minus_calculation_cents": (
                expected_difference_cents
            ),

            "official_total_fatura_cents": (
                official[
                    "total_fatura_cents"
                ]
            ),

            "official_total_ajustes_cents": (
                official[
                    "total_ajustes_cents"
                ]
            ),

            "official_valor_a_pagar_cents": (
                official[
                    "valor_a_pagar_cents"
                ]
            ),
        }

        self.logger.dados(
            "RESUMO DA FATURA",
            resumo,
        )

        if excluded_rows:
            self.logger.dados(
                "LANÇAMENTOS EXCLUÍDOS DO CÁLCULO",
                excluded_rows,
            )

        for row in rows:
            for problema in row[
                "debug_problems"
            ]:
                self.logger.problema(
                    codigo=problema,
                    descricao=(
                        "Problema detectado "
                        "durante auditoria de fatura."
                    ),
                    dados=row,
                )

            for warning in row[
                "debug_warnings"
            ]:
                self.logger.problema(
                    codigo=warning,
                    descricao=(
                        "Inconsistência potencial "
                        "detectada no lançamento."
                    ),
                    dados=row,
                )

        self.logger.fim_auditoria(
            tipo="FATURA",
            identificador=identificador,
            problemas_encontrados=(
                problemas_encontrados
            ),
        )

        return {
            "invoice": fatura,
            "credit_card": cartao,

            "summary": resumo,

            "rows": rows,

            "calculation_rows": (
                calculation_rows
            ),

            "excluded_rows": (
                excluded_rows
            ),

            "adjustments": (
                raw_adjustments
            ),

            "official": official,
        }

    # ============================================================
    # AUDITORIA DE GRUPO
    # ============================================================

    def auditar_grupo(
            self,
            installment_group_id: str,
    ) -> dict:

        rows = (
            self.repository
            .listar_lancamentos_grupo(
                installment_group_id
            )
        )

        if not rows:
            raise ValueError(
                "Grupo não encontrado: "
                f"{installment_group_id}"
            )

        self.logger.inicio_auditoria(
            tipo="INSTALLMENT_GROUP",
            identificador=(
                installment_group_id
            ),
        )

        problemas = []

        # --------------------------------------------------------
        # CARTÕES DIFERENTES
        # --------------------------------------------------------

        credit_card_ids = {
            row.get(
                "credit_card_id"
            )
            for row in rows
        }

        credit_card_ids.discard(
            None
        )

        if len(credit_card_ids) > 1:
            problemas.append(
                {
                    "code": "GROUP_MULTI_CARD",
                    "details": sorted(
                        credit_card_ids
                    ),
                }
            )

        # --------------------------------------------------------
        # INSTALLMENT TOTAL DIFERENTE
        # --------------------------------------------------------

        installment_totals = {
            row.get(
                "installment_total"
            )
            for row in rows
            if row.get(
                "installment_total"
            ) is not None
        }

        if len(installment_totals) > 1:
            problemas.append(
                {
                    "code": (
                        "GROUP_TOTAL_INCONSISTENT"
                    ),
                    "details": sorted(
                        installment_totals
                    ),
                }
            )

        # --------------------------------------------------------
        # PARCELA DUPLICADA ATIVA
        # --------------------------------------------------------

        por_numero = {}

        for row in rows:
            numero = row.get(
                "installment_number"
            )

            if numero not in por_numero:
                por_numero[numero] = []

            if row.get(
                    "status"
            ) != "cancelled":
                por_numero[numero].append(
                    row
                )

        for numero, parcelas in (
                por_numero.items()
        ):
            if len(parcelas) > 1:
                problemas.append(
                    {
                        "code": (
                            "DUPLICATE_INSTALLMENT"
                        ),
                        "installment_number": (
                            numero
                        ),
                        "expense_ids": [
                            row["id"]
                            for row in parcelas
                        ],
                    }
                )

        # --------------------------------------------------------
        # REAL + PROJETADA ATIVAS
        # --------------------------------------------------------

        for numero, parcelas in (
                por_numero.items()
        ):
            if not parcelas:
                continue

            projected = [
                row
                for row in parcelas
                if row.get(
                    "source_type"
                ) == "projected_installment"
            ]

            real = [
                row
                for row in parcelas
                if row.get(
                    "source_type"
                ) != "projected_installment"
            ]

            if projected and real:
                problemas.append(
                    {
                        "code": (
                            "PROJECTED_REAL_COLLISION"
                        ),
                        "installment_number": (
                            numero
                        ),
                        "projected_ids": [
                            row["id"]
                            for row in projected
                        ],
                        "real_ids": [
                            row["id"]
                            for row in real
                        ],
                    }
                )

        # --------------------------------------------------------
        # PARCELAS AUSENTES
        # --------------------------------------------------------

        ativos = [
            row
            for row in rows
            if row.get(
                "status"
            ) != "cancelled"
        ]

        if (
                len(installment_totals) == 1
                and ativos
        ):
            total = next(
                iter(
                    installment_totals
                )
            )

            existentes = {
                row.get(
                    "installment_number"
                )
                for row in ativos
            }

            faltantes = [
                numero
                for numero in range(
                    1,
                    total + 1,
                )
                if numero not in existentes
            ]

            if faltantes:
                problemas.append(
                    {
                        "code": (
                            "MISSING_INSTALLMENTS"
                        ),
                        "missing": faltantes,
                    }
                )

        # --------------------------------------------------------
        # CLASSIFICAÇÃO INDIVIDUAL
        # --------------------------------------------------------

        classified_rows = []

        for row in rows:
            classificacao = (
                self.classificar_lancamento(
                    row
                )
            )

            classified_rows.append(
                {
                    **row,
                    "debug_problems": (
                        classificacao[
                            "problems"
                        ]
                    ),
                    "debug_warnings": (
                        classificacao[
                            "warnings"
                        ]
                    ),
                    "expected_invoice": (
                        classificacao[
                            "expected_invoice"
                        ]
                    ),
                    "actual_invoice": (
                        classificacao[
                            "actual_invoice"
                        ]
                    ),
                }
            )

        for problema in problemas:
            self.logger.problema(
                codigo=problema["code"],
                descricao=(
                    "Problema detectado "
                    "no grupo de parcelamento."
                ),
                dados=problema,
            )

        self.logger.dados(
            "LANÇAMENTOS DO GRUPO",
            classified_rows,
        )

        self.logger.fim_auditoria(
            tipo="INSTALLMENT_GROUP",
            identificador=(
                installment_group_id
            ),
            problemas_encontrados=len(
                problemas
            ),
        )

        return {
            "installment_group_id": (
                installment_group_id
            ),
            "rows": classified_rows,
            "problems": problemas,
        }

    # ============================================================
    # AUDITORIA GLOBAL
    # ============================================================

    def auditar_problemas_globais(
            self,
    ) -> dict:

        self.logger.inicio_auditoria(
            tipo="GLOBAL",
            identificador="CREDIT_CARD_DATABASE",
        )

        sem_fatura = (
            self.repository
            .listar_lancamentos_sem_fatura()
        )

        fatura_inexistente = (
            self.repository
            .listar_lancamentos_com_fatura_inexistente()
        )

        cartao_divergente = (
            self.repository
            .listar_lancamentos_cartao_fatura_divergentes()
        )

        parcelas_duplicadas = (
            self.repository
            .listar_parcelas_duplicadas_no_grupo()
        )

        colisoes = (
            self.repository
            .listar_colisoes_real_projecao()
        )

        foreign_keys = (
            self.repository
            .executar_foreign_key_check()
        )

        resultado = {
            "no_invoice": sem_fatura,

            "orphan_invoice": (
                fatura_inexistente
            ),

            "card_invoice_mismatch": (
                cartao_divergente
            ),

            "duplicate_installments": (
                parcelas_duplicadas
            ),

            "projected_real_collisions": (
                colisoes
            ),

            "foreign_key_errors": (
                foreign_keys
            ),
        }

        total = sum(
            len(lista)
            for lista in resultado.values()
        )

        for codigo, dados in (
                resultado.items()
        ):
            if dados:
                self.logger.problema(
                    codigo=codigo.upper(),
                    descricao=(
                        f"{len(dados)} ocorrência(s)"
                    ),
                    dados=dados,
                )

        self.logger.fim_auditoria(
            tipo="GLOBAL",
            identificador=(
                "CREDIT_CARD_DATABASE"
            ),
            problemas_encontrados=total,
        )

        return {
            "total_problems": total,
            **resultado,
        }

    # ============================================================
    # ALTERAÇÃO MANUAL — GRUPO
    # ============================================================

    def mover_lancamento_para_grupo(
            self,
            expense_id: int,
            novo_installment_group_id: str | None,
    ) -> dict:

        antes = self.repository.buscar_lancamento(
            expense_id
        )

        if antes is None:
            raise ValueError(
                f"Lançamento não encontrado: "
                f"{expense_id}"
            )

        self.repository.alterar_installment_group_id(
            expense_id=expense_id,
            installment_group_id=(
                novo_installment_group_id
            ),
        )

        depois = self.repository.buscar_lancamento(
            expense_id
        )

        self.logger.alteracao(
            acao=(
                "ALTERAR_INSTALLMENT_GROUP_ID"
            ),
            entidade=(
                "finance_credit_card_expenses"
            ),
            identificador=expense_id,
            antes=antes,
            depois=depois,
        )

        return {
            "before": antes,
            "after": depois,
        }

    # ============================================================
    # ALTERAÇÃO MANUAL — FATURA
    # ============================================================

    def mover_lancamento_para_fatura(
            self,
            expense_id: int,
            novo_invoice_id: int | None,
    ) -> dict:

        antes = self.repository.buscar_lancamento(
            expense_id
        )

        if antes is None:
            raise ValueError(
                f"Lançamento não encontrado: "
                f"{expense_id}"
            )

        if novo_invoice_id is not None:
            fatura = self.repository.buscar_fatura(
                novo_invoice_id
            )

            if fatura is None:
                raise ValueError(
                    "Fatura de destino "
                    "não encontrada: "
                    f"{novo_invoice_id}"
                )

        self.repository.alterar_invoice_id(
            expense_id=expense_id,
            invoice_id=novo_invoice_id,
        )

        depois = self.repository.buscar_lancamento(
            expense_id
        )

        self.logger.alteracao(
            acao="ALTERAR_INVOICE_ID",
            entidade=(
                "finance_credit_card_expenses"
            ),
            identificador=expense_id,
            antes=antes,
            depois=depois,
        )

        return {
            "before": antes,
            "after": depois,
        }

    # ============================================================
    # CANCELAR / RESTAURAR
    # ============================================================

    def alterar_status_lancamento(
            self,
            expense_id: int,
            novo_status: str,
    ) -> dict:

        antes = self.repository.buscar_lancamento(
            expense_id
        )

        if antes is None:
            raise ValueError(
                f"Lançamento não encontrado: "
                f"{expense_id}"
            )

        self.repository.alterar_status_lancamento(
            expense_id=expense_id,
            status=novo_status,
        )

        depois = self.repository.buscar_lancamento(
            expense_id
        )

        self.logger.alteracao(
            acao="ALTERAR_STATUS",
            entidade=(
                "finance_credit_card_expenses"
            ),
            identificador=expense_id,
            antes=antes,
            depois=depois,
        )

        return {
            "before": antes,
            "after": depois,
        }

    # ============================================================
    # HELPERS
    # ============================================================

    def _obter_competencia_atual(
            self,
            lancamento: dict,
    ) -> tuple[int, int] | None:

        ano = lancamento.get(
            "invoice_year"
        )

        mes = lancamento.get(
            "invoice_month"
        )

        if ano is None or mes is None:
            return None

        return (
            int(ano),
            int(mes),
        )

    def _calcular_competencia_esperada(
            self,
            lancamento: dict,
    ) -> tuple[int, int] | None:

        data_raw = lancamento.get(
            "effective_purchase_date"
        )

        credit_card_id = lancamento.get(
            "credit_card_id"
        )

        if (
                not data_raw
                or credit_card_id is None
        ):
            return None

        cartao = self.repository.buscar_cartao(
            credit_card_id
        )

        if cartao is None:
            return None

        try:
            if isinstance(
                    data_raw,
                    datetime,
            ):
                purchase_date = (
                    data_raw.date()
                )

            elif isinstance(
                    data_raw,
                    date,
            ):
                purchase_date = data_raw

            else:
                purchase_date = (
                    date.fromisoformat(
                        str(data_raw)[:10]
                    )
                )

        except ValueError:
            return None

        return (
            self.detail_service
            .invoice_service
            .calcular_mes_fatura(
                purchase_date=(
                    purchase_date
                ),
                closing_day=cartao[
                    "closing_day"
                ],
            )
        )