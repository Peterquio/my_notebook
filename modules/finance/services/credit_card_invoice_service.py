from datetime import date
import calendar


class CreditCardInvoiceService:
    def calcular_mes_fatura(
            self,
            purchase_date: date,
            closing_day: int,
    ) -> tuple[int, int]:

        if purchase_date.day <= closing_day:
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