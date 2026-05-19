from datetime import date

from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)
from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)


class CreditCardDetailService:
    def __init__(self, username: str) -> None:
        self.expense_repository = CreditCardExpenseRepository(username)
        self.invoice_service = CreditCardInvoiceService()

    def carregar_fatura_atual(
            self,
            credit_card: dict,
    ) -> dict:

        hoje = date.today()

        invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
            purchase_date=hoje,
            closing_day=credit_card["closing_day"],
        )

        lancamentos = self.expense_repository.listar_lancamentos_por_fatura(
            credit_card_id=credit_card["id"],
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        rows = self._montar_rows_tabela(
            lancamentos
        )

        total_fatura_cents = sum(
            lancamento["amount_cents"]
            for lancamento in lancamentos
        )

        return {
            "invoice_year": invoice_year,
            "invoice_month": invoice_month,
            "total_fatura_cents": total_fatura_cents,
            "total_lancamentos": len(lancamentos),
            "rows": rows,
        }

    def _montar_rows_tabela(
            self,
            lancamentos: list[dict],
    ) -> list[dict]:

        rows = []
        categoria_atual = None

        for lancamento in lancamentos:
            categoria = lancamento["category_name"] or "Sem categoria"
            cor = lancamento["category_color"] or "#6d28d9"

            if categoria != categoria_atual:
                categoria_atual = categoria

                rows.append(
                    {
                        "type": "group",
                        "name": categoria,
                        "icon": "■",
                        "count": "",
                        "total": "",
                        "color": cor,
                        "background": "#f8fafc",
                    }
                )

            valor_parcela = lancamento["amount_cents"]
            parcela_atual = lancamento["installment_number"]
            total_parcelas = lancamento["installment_total"]

            if total_parcelas > 1:
                parcelas_restantes = total_parcelas - parcela_atual + 1
                valor_restante = valor_parcela * parcelas_restantes
                texto_restante = self._formatar_moeda(valor_restante)
                texto_parcela = f"{parcela_atual:02d}/{total_parcelas:02d}"
            else:
                texto_restante = "-"
                texto_parcela = "-"

            rows.append(
                {
                    "type": "expense",
                    "date": self._formatar_data_curta(
                        lancamento["purchase_date"]
                    ),
                    "description": lancamento["description"],
                    "category": categoria,
                    "category_color": cor,
                    "installment": texto_parcela,
                    "remaining": texto_restante,
                    "amount": self._formatar_moeda(valor_parcela),
                }
            )

        return rows

    def _formatar_moeda(
            self,
            amount_cents: int,
    ) -> str:

        valor = amount_cents / 100

        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data_curta(
            self,
            data_iso: str,
    ) -> str:

        ano, mes, dia = data_iso.split("-")

        return f"{dia}/{mes}"