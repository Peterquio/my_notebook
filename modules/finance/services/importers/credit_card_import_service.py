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

    def confirmar_importacao(
            self,
            credit_card: dict,
            expenses: list[ImportedCreditCardExpense],
            category_id: int = 1,
    ) -> int:

        total_salvo = 0

        for expense in expenses:
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
                description=expense.description,
                purchase_date=expense.purchase_date.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=expense.installment_number,
                installment_total=expense.installment_total,
                amount_cents=expense.amount_cents,
                original_expense_group_id=expense.raw_title,
                notes=f"Importado via CSV - {expense.source}",
            )

            total_salvo += 1

        return total_salvo