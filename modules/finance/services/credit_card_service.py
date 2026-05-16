from datetime import date

from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)

from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)

from modules.finance.repositories.credit_card_repository import (
    CreditCardRepository,
)

class CreditCardService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = CreditCardRepository(
            username
        )
        self.expense_repository = CreditCardExpenseRepository(
            username
        )
        self.invoice_service = CreditCardInvoiceService()

    def listar_assets(self) -> list[dict]:
        return self.repository.listar_assets()

    def criar_cartao(
            self,
            dashboard_card_id: str,
            name: str,
            asset_id: str,
            limit_amount_cents: int,
            closing_day: int,
            due_day: int,
            last_four_digits: str | None = None,
    ) -> int:

        return self.repository.criar_cartao(
            dashboard_card_id=dashboard_card_id,
            name=name,
            asset_id=asset_id,
            limit_amount_cents=limit_amount_cents,
            closing_day=closing_day,
            due_day=due_day,
            last_four_digits=last_four_digits,
        )

    def buscar_por_dashboard_card_id(
            self,
            dashboard_card_id: str,
    ) -> dict | None:

        return self.repository.buscar_por_dashboard_card_id(
            dashboard_card_id
        )

    def obter_total_fatura_atual(
            self,
            credit_card_id: int,
            closing_day: int,
    ) -> int:
        hoje = date.today()

        invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
            purchase_date=hoje,
            closing_day=closing_day,
        )

        return self.expense_repository.somar_fatura(
            credit_card_id=credit_card_id,
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

    def listar_cartoes_ativos(self) -> list[dict]:
        return self.repository.listar_cartoes_ativos()
