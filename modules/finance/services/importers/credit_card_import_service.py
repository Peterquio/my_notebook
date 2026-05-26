from collections import Counter, defaultdict
from modules.finance.repositories.credit_card_invoice_repository import (
    CreditCardInvoiceRepository,
)
from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)
from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)
from modules.finance.services.importers.credit_card_csv_import_handler import (
    CreditCardCsvImportHandler,
)
from modules.finance.services.importers.credit_card_csv_converters import (
    ImportedCreditCardExpense,
)


class CreditCardImportService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.csv_handler = CreditCardCsvImportHandler()
        self.invoice_repository = CreditCardInvoiceRepository(username)
        self.expense_repository = CreditCardExpenseRepository(username)
        self.invoice_service = CreditCardInvoiceService()

    def importar_preview(
            self,
            csv_path: str,
    ) -> list[ImportedCreditCardExpense]:

        return self.csv_handler.import_preview(
            csv_path
        )

    def _gerar_assinatura_importacao(
            self,
            expense: ImportedCreditCardExpense,
    ) -> tuple:
        return (
            expense.raw_title,
            expense.purchase_date.isoformat(),
            expense.amount_cents,
            expense.installment_number,
            expense.installment_total,
        )

    def confirmar_importacao(
            self,
            credit_card: dict,
            expenses: list[ImportedCreditCardExpense],
            category_id: int = 1,
    ) -> int:

        total_salvo = 0

        total_por_assinatura = Counter(
            self._gerar_assinatura_importacao(expense)
            for expense in expenses
        )

        ja_importados_agora = defaultdict(int)

        for expense in expenses:
            assinatura = self._gerar_assinatura_importacao(expense)

            total_no_banco = self.expense_repository.contar_lancamentos_por_assinatura(
                credit_card_id=credit_card["id"],
                original_description=assinatura[0],
                original_purchase_date=assinatura[1],
                original_amount_cents=assinatura[2],
                installment_number=assinatura[3],
                installment_total=assinatura[4],
            )

            if total_no_banco + ja_importados_agora[assinatura] >= total_por_assinatura[assinatura]:
                continue

            invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
                purchase_date=expense.purchase_date,
                closing_day=credit_card["closing_day"],
            )

            closing_date = self.invoice_service.montar_data_segura(
                invoice_year,
                invoice_month,
                credit_card["closing_day"],
            )

            due_date = self.invoice_service.montar_data_segura(
                invoice_year,
                invoice_month,
                credit_card["due_day"],
            )

            invoice = self.invoice_repository.buscar_por_cartao_mes(
                credit_card_id=credit_card["id"],
                invoice_year=invoice_year,
                invoice_month=invoice_month,
            )

            if invoice is None:
                invoice_id = self.invoice_repository.criar_fatura(
                    credit_card_id=credit_card["id"],
                    invoice_year=invoice_year,
                    invoice_month=invoice_month,
                    closing_date=closing_date.isoformat(),
                    due_date=due_date.isoformat(),
                )
            else:
                invoice_id = invoice["id"]

            self.expense_repository.criar_lancamento(
                credit_card_id=credit_card["id"],
                invoice_id=invoice_id,
                category_id=category_id,
                effective_description=expense.description,
                effective_purchase_date=expense.purchase_date.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=expense.installment_number,
                installment_total=expense.installment_total,
                effective_amount_cents=expense.amount_cents,
                installment_group_id=expense.raw_title,
                notes=f"Importado via CSV - {expense.source}",
                original_description=expense.raw_title,
                original_purchase_date=expense.purchase_date.isoformat(),
                original_amount_cents=expense.amount_cents,
                source_type=expense.source,
                source_reference=expense.raw_title,
            )

            ja_importados_agora[assinatura] += 1
            total_salvo += 1

        return total_salvo