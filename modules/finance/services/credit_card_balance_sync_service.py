from datetime import date

from modules.finance.repositories.balance_repository import BalanceRepository
from modules.finance.repositories.credit_card_repository import CreditCardRepository

from modules.finance.repositories.credit_card_invoice_repository import (
    CreditCardInvoiceRepository,
)

from modules.finance.services.balance_service import BalanceService

from modules.finance.services.credit_card_detail_service import (
    CreditCardDetailService,
)

from modules.finance.repositories.credit_card_invoice_adjustment_repository import (
    CreditCardInvoiceAdjustmentRepository,
)



class CreditCardBalanceSyncService:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.username = username

        self.balance_repository = BalanceRepository(
            username
        )

        self.balance_service = BalanceService(
            username
        )

        self.credit_card_repository = CreditCardRepository(
            username
        )

        self.invoice_repository = CreditCardInvoiceRepository(
            username
        )

        self.detail_service = CreditCardDetailService(
            username
        )

        self.adjustment_repository = (
            CreditCardInvoiceAdjustmentRepository(
                username
            )
        )

    def sincronizar_fatura_com_saldo(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
            sync_mode: str = "open",
    ) -> list[int]:
        credit_card = self._buscar_cartao_por_id(
            credit_card_id
        )

        if credit_card is None:
            raise ValueError(
                f"Cartão não encontrado: {credit_card_id}"
            )

        if credit_card["sync_with_balance"] != 1:
            return []

        if credit_card["account_id"] is None:
            return []

        invoice_data = self.detail_service.carregar_fatura_por_mes(
            credit_card=credit_card,
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        valor_a_pagar_cents = int(
            invoice_data["valor_a_pagar_cents"] or 0
        )

        ajustes = self.adjustment_repository.listar_ajustes_fatura(
            credit_card_id=credit_card_id,
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        due_date = self._calcular_data_vencimento(
            invoice_year=invoice_year,
            invoice_month=invoice_month,
            due_day=credit_card["due_day"],
        )

        cycle = self._obter_ou_criar_ciclo_por_data(
            due_date
        )

        compromisso_ids = []
        referencias_pagamentos_atuais = set()

        for ajuste in ajustes:
            if ajuste["adjustment_type"] != "payment_received":
                continue

            valor_pago_cents = abs(
                int(ajuste["amount_cents"] or 0)
            )

            if valor_pago_cents <= 0:
                continue

            external_reference = (
                f"cc:{credit_card_id}:"
                f"{invoice_year}:"
                f"{invoice_month:02d}:"
                f"payment:{ajuste['id']}"
            )

            referencias_pagamentos_atuais.add(
                external_reference
            )

            description = (
                f"Fatura {credit_card['name']} "
                f"{invoice_month:02d}/{invoice_year} "
                f"— pagamento {self._formatar_data_br(ajuste['adjustment_date'])}"
            )

            compromisso_id = (
                self.balance_repository.upsert_compromisso_por_external_reference(
                    external_reference=external_reference,
                    cycle_id=cycle["id"],
                    description=description,
                    expected_amount_cents=valor_pago_cents,
                    actual_amount_cents=valor_pago_cents,
                    due_date=ajuste["adjustment_date"],
                    paid_date=ajuste["adjustment_date"],
                    payment_type="credit_card",
                    account_id=credit_card["account_id"],
                    credit_card_id=credit_card_id,
                    status="paid",
                    commitment_origin="credit_card_closed",
                    projection_type="real",
                    is_recurring=False,
                    notes="Pagamento de fatura sincronizado automaticamente pelo cartão de crédito.",
                )
            )

            compromisso_ids.append(
                compromisso_id
            )

        self._remover_pagamentos_sincronizados_que_nao_existem_mais(
            credit_card_id=credit_card_id,
            invoice_year=invoice_year,
            invoice_month=invoice_month,
            referencias_pagamentos_atuais=referencias_pagamentos_atuais,
        )

        external_reference_open = (
            f"cc:{credit_card_id}:"
            f"{invoice_year}:"
            f"{invoice_month:02d}:"
            f"open"
        )

        commitment_origin = (
            "credit_card_open"
            if sync_mode == "open"
            else "credit_card_projected"
        )

        projection_type = (
            "real"
            if sync_mode == "open"
            else "projected"
        )

        if valor_a_pagar_cents > 0:
            description = (
                f"Fatura {credit_card['name']} "
                f"{invoice_month:02d}/{invoice_year} "
                f"— saldo em aberto"
            )

            compromisso_id = (
                self.balance_repository.upsert_compromisso_por_external_reference(
                    external_reference=external_reference_open,
                    cycle_id=cycle["id"],
                    description=description,
                    expected_amount_cents=valor_a_pagar_cents,
                    actual_amount_cents=None,
                    due_date=due_date,
                    paid_date=None,
                    payment_type="credit_card",
                    account_id=credit_card["account_id"],
                    credit_card_id=credit_card_id,
                    status="expected",
                    commitment_origin=commitment_origin,
                    projection_type=projection_type,
                    is_recurring=False,
                    notes="Saldo em aberto da fatura sincronizado automaticamente pelo cartão de crédito.",
                )
            )

            compromisso_ids.append(
                compromisso_id
            )
        else:
            self._excluir_compromisso_por_external_reference(
                external_reference_open
            )

        return compromisso_ids

    def sincronizar_todos_cartoes_para_saldo(
            self,
    ) -> list[int]:
        hoje = date.today()
        compromisso_ids = []

        for cartao in self.credit_card_repository.listar_cartoes_ativos():
            if cartao["sync_with_balance"] != 1:
                continue

            if cartao["account_id"] is None:
                continue

            ultima_fatura = (
                self.invoice_repository.buscar_ultima_fatura_cartao(
                    cartao["id"]
                )
            )

            if ultima_fatura is None:
                continue

            ano_atual = hoje.year
            mes_atual = hoje.month

            ano_final = int(ultima_fatura["invoice_year"])
            mes_final = int(ultima_fatura["invoice_month"])

            ano = ano_atual
            mes = mes_atual

            while (
                    ano < ano_final
                    or (
                            ano == ano_final
                            and mes <= mes_final
                    )
            ):
                sync_mode = (
                    "open"
                    if (
                            ano == ano_atual
                            and mes == mes_atual
                    )
                    else "projection"
                )

                ids_criados = self.sincronizar_fatura_com_saldo(
                    credit_card_id=cartao["id"],
                    invoice_year=ano,
                    invoice_month=mes,
                    sync_mode=sync_mode,
                )

                compromisso_ids.extend(
                    ids_criados
                )

                if mes == 12:
                    ano += 1
                    mes = 1
                else:
                    mes += 1

        return compromisso_ids

    def _remover_pagamentos_sincronizados_que_nao_existem_mais(
            self,
            credit_card_id: int,
            invoice_year: int,
            invoice_month: int,
            referencias_pagamentos_atuais: set[str],
    ) -> None:
        prefixo_pagamento = (
            f"cc:{credit_card_id}:"
            f"{invoice_year}:"
            f"{invoice_month:02d}:"
            f"payment:"
        )

        compromissos_sincronizados = (
            self.balance_repository.listar_compromissos_por_prefixo_external_reference(
                prefixo_pagamento
            )
        )

        for compromisso in compromissos_sincronizados:
            external_reference = compromisso["external_reference"]

            if external_reference in referencias_pagamentos_atuais:
                continue

            self.balance_repository.excluir_compromisso(
                compromisso["id"]
            )

    def _excluir_compromisso_por_external_reference(
            self,
            external_reference: str,
    ) -> None:
        compromisso = (
            self.balance_repository.buscar_compromisso_por_external_reference(
                external_reference
            )
        )

        if compromisso is None:
            return

        self.balance_repository.excluir_compromisso(
            compromisso["id"]
        )

    def _formatar_data_br(
            self,
            data_iso: str,
    ) -> str:
        ano, mes, dia = data_iso.split("-")

        return f"{dia}/{mes}/{ano}"

    def _buscar_cartao_por_id(
            self,
            credit_card_id: int,
    ) -> dict | None:
        for card in self.credit_card_repository.listar_cartoes_ativos():
            if card["id"] == credit_card_id:
                return card

        return None

    def _obter_ou_criar_ciclo_por_data(
            self,
            data_iso: str,
    ) -> dict:
        ciclo = self._encontrar_ciclo_por_data(
            data_iso
        )

        if ciclo is not None:
            return ciclo

        ciclos = self.balance_repository.listar_ciclos_ativos()

        if not ciclos:
            raise ValueError(
                "Nenhum ciclo financeiro foi criado ainda. "
                "Crie o primeiro ciclo no módulo Saldo antes de sincronizar faturas."
            )

        ciclos_ordenados = sorted(
            ciclos,
            key=lambda item: item["start_date"],
        )

        ultimo_ciclo = ciclos_ordenados[-1]

        data_referencia = date.fromisoformat(
            data_iso
        )

        while data_referencia > date.fromisoformat(ultimo_ciclo["end_date"]):
            novo_cycle_id = self.balance_service.gerar_proximo_ciclo_real(
                ultimo_ciclo["id"]
            )

            novo_ciclo = self.balance_repository.buscar_ciclo_por_id(
                novo_cycle_id
            )

            if novo_ciclo is None:
                raise ValueError(
                    "O ciclo financeiro foi criado, mas não pôde ser carregado."
                )

            ultimo_ciclo = novo_ciclo

        return ultimo_ciclo

    def _calcular_fim_proximo_ciclo(
            self,
            start_date: date,
    ) -> date:
        if start_date.day == 1:
            return date(
                start_date.year,
                start_date.month,
                self._ultimo_dia_mes(
                    start_date.year,
                    start_date.month,
                ),
            )

        proximo_mes_year, proximo_mes_month = self._somar_meses_competencia(
            year=start_date.year,
            month=start_date.month,
            deslocamento=1,
        )

        ultimo_dia_mes_destino = self._ultimo_dia_mes(
            proximo_mes_year,
            proximo_mes_month,
        )

        dia_fim = min(
            start_date.day - 1,
            ultimo_dia_mes_destino,
        )

        return date(
            proximo_mes_year,
            proximo_mes_month,
            dia_fim,
        )

    def _montar_nome_ciclo(
            self,
            start_date: date,
    ) -> str:
        return f"Ciclo {start_date.month:02d}/{start_date.year}"


    def _encontrar_ciclo_por_data(
            self,
            data_iso: str,
    ) -> dict | None:
        data_referencia = date.fromisoformat(
            data_iso
        )

        ciclos = self.balance_repository.listar_ciclos_ativos()

        for ciclo in ciclos:
            start_date = date.fromisoformat(
                ciclo["start_date"]
            )
            end_date = date.fromisoformat(
                ciclo["end_date"]
            )

            if start_date <= data_referencia <= end_date:
                return ciclo

        return None

    def _calcular_data_vencimento(
            self,
            invoice_year: int,
            invoice_month: int,
            due_day: int,
    ) -> str:
        ultimo_dia_mes = self._ultimo_dia_mes(
            invoice_year,
            invoice_month,
        )

        dia = min(
            due_day,
            ultimo_dia_mes,
        )

        return date(
            invoice_year,
            invoice_month,
            dia,
        ).isoformat()

    def _ultimo_dia_mes(
            self,
            year: int,
            month: int,
    ) -> int:
        if month == 12:
            proximo_mes = date(year + 1, 1, 1)
        else:
            proximo_mes = date(year, month + 1, 1)

        ultimo_dia = proximo_mes.replace(day=1).toordinal() - 1

        return date.fromordinal(
            ultimo_dia
        ).day

    def _somar_meses_competencia(
            self,
            year: int,
            month: int,
            deslocamento: int,
    ) -> tuple[int, int]:
        mes_total = month - 1 + deslocamento
        novo_ano = year + mes_total // 12
        novo_mes = mes_total % 12 + 1

        return novo_ano, novo_mes