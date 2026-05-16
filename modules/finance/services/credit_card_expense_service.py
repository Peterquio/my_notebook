from datetime import date
import uuid

from modules.finance.repositories.credit_card_invoice_repository import (
    CreditCardInvoiceRepository,
)
from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)
from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)


class CreditCardExpenseService:
    def __init__(self, username: str) -> None:
        self.invoice_repository = CreditCardInvoiceRepository(username)
        self.expense_repository = CreditCardExpenseRepository(username)
        self.invoice_service = CreditCardInvoiceService()

    def registrar_compra(
            self,
            credit_card_id: int,
            description: str,
            purchase_date: date,
            amount_cents: int,
            closing_day: int,
            due_day: int,
            category_id: int = 1,
            installment_total: int = 1,
            notes: str | None = None,
    ) -> list[int]:

        group_id = str(uuid.uuid4())
        lancamentos_criados = []

        valor_base = amount_cents // installment_total
        resto = amount_cents % installment_total

        for parcela in range(1, installment_total + 1):
            invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
                purchase_date=purchase_date,
                closing_day=closing_day,
            )

            invoice_month += parcela - 1

            while invoice_month > 12:
                invoice_month -= 12
                invoice_year += 1

            closing_date = self.invoice_service.montar_data_segura(
                invoice_year,
                invoice_month,
                closing_day,
            )

            due_date = self.invoice_service.montar_data_segura(
                invoice_year,
                invoice_month,
                due_day,
            )

            invoice = self.invoice_repository.buscar_por_cartao_mes(
                credit_card_id=credit_card_id,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
            )

            if invoice is None:
                invoice_id = self.invoice_repository.criar_fatura(
                    credit_card_id=credit_card_id,
                    invoice_year=invoice_year,
                    invoice_month=invoice_month,
                    closing_date=closing_date.isoformat(),
                    due_date=due_date.isoformat(),
                )
            else:
                invoice_id = invoice["id"]

            valor_parcela = valor_base

            if parcela == installment_total:
                valor_parcela += resto

            lancamento_id = self.expense_repository.criar_lancamento(
                credit_card_id=credit_card_id,
                invoice_id=invoice_id,
                category_id=category_id,
                description=description,
                purchase_date=purchase_date.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=parcela,
                installment_total=installment_total,
                amount_cents=valor_parcela,
                original_expense_group_id=group_id,
                notes=notes,
            )

            lancamentos_criados.append(lancamento_id)

        return lancamentos_criados