from datetime import date

from modules.finance.repositories.balance_repository import BalanceRepository
from modules.finance.repositories.credit_card_repository import CreditCardRepository

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

        self.credit_card_repository = CreditCardRepository(
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
                    is_recurring=False,
                    notes="Pagamento de fatura sincronizado automaticamente pelo cartão de crédito.",
                )
            )

            compromisso_ids.append(
                compromisso_id
            )

        if valor_a_pagar_cents > 0:
            external_reference = (
                f"cc:{credit_card_id}:"
                f"{invoice_year}:"
                f"{invoice_month:02d}:"
                f"open"
            )

            description = (
                f"Fatura {credit_card['name']} "
                f"{invoice_month:02d}/{invoice_year} "
                f"— saldo em aberto"
            )

            compromisso_id = (
                self.balance_repository.upsert_compromisso_por_external_reference(
                    external_reference=external_reference,
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
                    is_recurring=False,
                    notes="Saldo em aberto da fatura sincronizado automaticamente pelo cartão de crédito.",
                )
            )

            compromisso_ids.append(
                compromisso_id
            )

        return compromisso_ids

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

        start_date = date.fromisoformat(
            ultimo_ciclo["start_date"]
        )

        end_date = date.fromisoformat(
            ultimo_ciclo["end_date"]
        )

        while data_referencia > end_date:
            novo_start = end_date.fromordinal(
                end_date.toordinal() + 1
            )

            novo_end = self._calcular_fim_proximo_ciclo(
                novo_start
            )

            nome = self._montar_nome_ciclo(
                novo_start
            )

            cycle_id = self.balance_repository.criar_ciclo(
                name=nome,
                start_date=novo_start.isoformat(),
                end_date=novo_end.isoformat(),
                opening_balance_source="auto",
            )

            ultimo_ciclo = self.balance_repository.buscar_ciclo_por_id(
                cycle_id
            )

            if ultimo_ciclo is None:
                raise ValueError(
                    "O ciclo financeiro foi criado, mas não pôde ser carregado."
                )

            start_date = date.fromisoformat(
                ultimo_ciclo["start_date"]
            )

            end_date = date.fromisoformat(
                ultimo_ciclo["end_date"]
            )

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