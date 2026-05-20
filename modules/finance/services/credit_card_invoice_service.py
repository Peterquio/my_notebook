from datetime import date
import calendar


class CreditCardInvoiceService:
    def calcular_mes_fatura(
            self,
            purchase_date: date,
            closing_day: int,
    ) -> tuple[int, int]:

        if purchase_date.day < closing_day:
            return purchase_date.year, purchase_date.month

        next_month = purchase_date.month + 1
        year = purchase_date.year

        if next_month > 12:
            next_month = 1
            year += 1

        return year, next_month

    def montar_data_segura(
            self,
            year: int,
            month: int,
            day: int,
    ) -> date:

        ultimo_dia = calendar.monthrange(
            year,
            month,
        )[1]

        dia_final = min(
            day,
            ultimo_dia,
        )

        return date(
            year,
            month,
            dia_final,
        )

    def reprocessar_faturas_cartao(
            self,
            credit_card: dict,
            expense_repository,
            invoice_repository,
    ) -> int:

        lancamentos = expense_repository.listar_por_cartao(
            credit_card["id"]
        )

        total_reprocessado = 0

        for lancamento in lancamentos:
            purchase_date = date.fromisoformat(
                lancamento["purchase_date"]
            )

            invoice_year, invoice_month = self.calcular_mes_fatura(
                purchase_date=purchase_date,
                closing_day=credit_card["closing_day"],
            )

            invoice = invoice_repository.buscar_por_cartao_mes(
                credit_card_id=credit_card["id"],
                invoice_year=invoice_year,
                invoice_month=invoice_month,
            )

            if invoice is None:
                closing_date = self.montar_data_segura(
                    invoice_year,
                    invoice_month,
                    credit_card["closing_day"],
                )

                due_date = self.montar_data_segura(
                    invoice_year,
                    invoice_month,
                    credit_card["due_day"],
                )

                invoice_id = invoice_repository.criar_fatura(
                    credit_card_id=credit_card["id"],
                    invoice_year=invoice_year,
                    invoice_month=invoice_month,
                    closing_date=closing_date.isoformat(),
                    due_date=due_date.isoformat(),
                )

            else:
                invoice_id = invoice["id"]

            expense_repository.atualizar_invoice_id(
                expense_id=lancamento["id"],
                invoice_id=invoice_id,
            )

            total_reprocessado += 1

        return total_reprocessado