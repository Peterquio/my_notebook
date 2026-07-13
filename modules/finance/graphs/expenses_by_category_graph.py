from datetime import date

from modules.finance.graphs.base_finance_graph import (
    BaseFinanceGraph,
)

from modules.finance.repositories.finance_graph_repository import (
    FinanceGraphRepository,
)

from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)

from modules.finance.services.subscription_service import (
    SubscriptionService,
)


class ExpensesByCategoryGraph(BaseFinanceGraph):
    graph_id = "expenses_by_category"
    title = "Gastos por Categoria"

    UNCATEGORIZED_NAME = "Sem categoria"
    UNCATEGORIZED_COLOR = "#9CA3AF"

    def __init__(
            self,
            username: str,
    ) -> None:

        super().__init__(
            username
        )

        self.repository = FinanceGraphRepository(
            username
        )

        self.invoice_service = CreditCardInvoiceService()

        self.subscription_service = SubscriptionService(
            username
        )

    def carregar_dados(
            self,
            start_date: str,
            end_date: str,
    ) -> dict:

        receitas = self.repository.listar_receitas_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        compromissos = self.repository.listar_compromissos_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        despesas_cartao = (
            self.repository.listar_despesas_cartao_por_vencimento(
                start_date=start_date,
                end_date=end_date,
            )
        )

        despesas_cartao_sem_fatura = (
            self._listar_despesas_cartao_sem_fatura_periodo(
                start_date=start_date,
                end_date=end_date,
            )
        )

        projecoes_assinaturas = (
            self.subscription_service.listar_projecoes_periodo(
                start_date=start_date,
                end_date=end_date,
            )
        )

        income_cents = self._somar_receitas(
            receitas
        )

        category_totals = {}

        self._acumular_itens(
            category_totals=category_totals,
            items=compromissos,
            source="balance_commitment",
        )

        self._acumular_itens(
            category_totals=category_totals,
            items=despesas_cartao,
            source="credit_card_expense",
        )

        self._acumular_itens(
            category_totals=category_totals,
            items=despesas_cartao_sem_fatura,
            source="credit_card_expense_without_invoice",
        )

        self._acumular_projecoes_assinaturas(
            category_totals=category_totals,
            projections=projecoes_assinaturas,
        )

        categories = self._ordenar_categorias(
            category_totals
        )

        expense_cents = sum(
            category["amount_cents"]
            for category in categories
        )

        return {
            "graph_id": self.graph_id,
            "title": self.title,

            "start_date": start_date,
            "end_date": end_date,

            "income_cents": income_cents,
            "expense_cents": expense_cents,

            "categories": categories,

            "metadata": {
                "income_count": len(receitas),
                "balance_expense_count": len(compromissos),
                "credit_card_expense_count": (
                    len(despesas_cartao)
                    + len(despesas_cartao_sem_fatura)
                ),
                "subscription_projection_count": (
                    self._contar_projecoes_assinaturas(
                        projecoes_assinaturas
                    )
                ),
            },
        }

    def _contar_projecoes_assinaturas(
            self,
            projections: list[dict],
    ) -> int:

        total = 0

        for projection in projections:
            details = projection.get(
                "details"
            ) or []

            if details:
                total += len(details)
                continue

            total += 1

        return total

    def _somar_receitas(
            self,
            receitas: list[dict],
    ) -> int:

        total = 0

        for receita in receitas:
            valor = int(
                receita.get("amount_cents") or 0
            )

            if valor <= 0:
                continue

            total += valor

        return total

    def _acumular_itens(
            self,
            category_totals: dict,
            items: list[dict],
            source: str,
    ) -> None:

        for item in items:
            amount_cents = int(
                item.get("amount_cents") or 0
            )

            if amount_cents <= 0:
                continue

            category_id = item.get(
                "category_id"
            )

            category_name = (
                item.get("category_name")
                or self.UNCATEGORIZED_NAME
            )

            category_color = (
                item.get("category_color")
                or self.UNCATEGORIZED_COLOR
            )

            key = (
                category_id
                if category_id is not None
                else "uncategorized"
            )

            if key not in category_totals:
                category_totals[key] = {
                    "category_id": category_id,
                    "name": category_name,
                    "color": category_color,
                    "amount_cents": 0,
                    "items_count": 0,
                    "is_uncategorized": category_id is None,
                    "items": [],
                }

            category_totals[key]["amount_cents"] += (
                amount_cents
            )

            category_totals[key]["items_count"] += 1

            category_totals[key]["items"].append(
                {
                    "id": (
                        item.get("expense_id")
                        or item.get("id")
                    ),
                    "description": (
                        item.get("description")
                        or "Lançamento"
                    ),
                    "date": item.get("event_date"),
                    "amount_cents": amount_cents,
                    "source": source,
                    "status": item.get("status"),
                }
            )

    def _acumular_projecoes_assinaturas(
            self,
            category_totals: dict,
            projections: list[dict],
    ) -> None:

        for projection in projections:
            details = projection.get(
                "details"
            ) or []

            if details:
                self._acumular_detalhes_assinaturas_agrupadas(
                    category_totals=category_totals,
                    projection=projection,
                    details=details,
                )
                continue

            self._acumular_assinatura_projetada(
                category_totals=category_totals,
                subscription_id=projection.get(
                    "subscription_id"
                ),
                description=projection.get(
                    "description",
                    "Assinatura prevista",
                ),
                event_date=projection.get("date"),
                amount_cents=int(
                    projection.get("amount_cents") or 0
                ),
                status=projection.get("status"),
            )

    def _acumular_detalhes_assinaturas_agrupadas(
            self,
            category_totals: dict,
            projection: dict,
            details: list[dict],
    ) -> None:

        for detail in details:
            self._acumular_assinatura_projetada(
                category_totals=category_totals,
                subscription_id=detail.get(
                    "subscription_id"
                ),
                description=detail.get(
                    "description",
                    "Assinatura prevista",
                ),
                event_date=projection.get("date"),
                amount_cents=int(
                    detail.get("amount_cents") or 0
                ),
                status=projection.get("status"),
            )

    def _acumular_assinatura_projetada(
            self,
            category_totals: dict,
            subscription_id: int | None,
            description: str,
            event_date: str | None,
            amount_cents: int,
            status: str | None,
    ) -> None:

        if amount_cents <= 0:
            return

        key = "uncategorized"

        if key not in category_totals:
            category_totals[key] = {
                "category_id": None,
                "name": self.UNCATEGORIZED_NAME,
                "color": self.UNCATEGORIZED_COLOR,
                "amount_cents": 0,
                "items_count": 0,
                "is_uncategorized": True,
                "items": [],
            }

        category_totals[key]["amount_cents"] += (
            amount_cents
        )

        category_totals[key]["items_count"] += 1

        category_totals[key]["items"].append(
            {
                "id": subscription_id,
                "description": description,
                "date": event_date,
                "amount_cents": amount_cents,
                "source": "subscription_projection",
                "status": status,
            }
        )

    def _listar_despesas_cartao_sem_fatura_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:

        despesas = (
            self.repository.listar_despesas_cartao_sem_fatura()
        )

        resultado = []

        for despesa in despesas:
            purchase_date = date.fromisoformat(
                despesa["effective_purchase_date"]
            )

            invoice_year, invoice_month = (
                self.invoice_service.calcular_mes_fatura(
                    purchase_date=purchase_date,
                    closing_day=int(
                        despesa["closing_day"]
                    ),
                )
            )

            due_date = (
                self.invoice_service.montar_data_segura(
                    year=invoice_year,
                    month=invoice_month,
                    day=int(
                        despesa["due_day"]
                    ),
                )
            )

            due_date_iso = due_date.isoformat()

            if not start_date <= due_date_iso <= end_date:
                continue

            item = dict(
                despesa
            )

            item["event_date"] = due_date_iso
            item["invoice_year"] = invoice_year
            item["invoice_month"] = invoice_month

            resultado.append(
                item
            )

        return resultado

    def _ordenar_categorias(
            self,
            category_totals: dict,
    ) -> list[dict]:

        categories = [
            category
            for category in category_totals.values()
            if category["amount_cents"] > 0
        ]

        categories.sort(
            key=lambda category: (
                -category["amount_cents"],
                category["name"].lower(),
            )
        )

        return categories