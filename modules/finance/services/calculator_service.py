from modules.finance.repositories.calculator_repository import (
    CalculatorRepository,
)


class CalculatorService:
    VALID_SIMULATION_TYPES = {
        "statement",
        "sum_values",
    }

    VALID_PERIOD_MODES = {
        "one_month",
        "free_period",
    }

    VALID_ITEM_KINDS = {
        "income",
        "expense",
        "neutral",
    }

    def __init__(
            self,
            username: str,
    ) -> None:

        self.repository = CalculatorRepository(username)

    def criar_simulacao(
            self,
            name: str,
            simulation_type: str,
            period_mode: str,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> int:

        name = name.strip()

        if not name:
            raise ValueError("Informe o nome da simulação.")

        self._validar_simulation_type(simulation_type)
        self._validar_period_mode(period_mode)

        return self.repository.criar_simulacao(
            name=name,
            simulation_type=simulation_type,
            period_mode=period_mode,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )

    def listar_simulacoes(self) -> list[dict]:
        return self.repository.listar_simulacoes(
            active_only=True,
        )

    def buscar_simulacao_com_itens(
            self,
            simulation_id: int,
    ) -> dict | None:

        simulacao = self.repository.buscar_simulacao(
            simulation_id
        )

        if simulacao is None:
            return None

        itens = self.repository.listar_itens(
            simulation_id
        )

        simulacao["items"] = itens
        simulacao["summary"] = self.calcular_resumo(
            simulation_type=simulacao["simulation_type"],
            items=itens,
        )

        return simulacao

    def excluir_simulacao(
            self,
            simulation_id: int,
    ) -> None:

        self.repository.desativar_simulacao(
            simulation_id
        )

    def criar_item(
            self,
            simulation_id: int,
            title: str,
            kind: str,
            item_date: str | None,
            amount_cents: int,
            sort_order: int = 0,
            notes: str | None = None,
    ) -> int:

        title = title.strip()

        if not title:
            raise ValueError("Informe o título do item.")

        self._validar_item_kind(kind)

        if amount_cents < 0:
            raise ValueError("O valor não pode ser negativo.")

        simulacao = self.repository.buscar_simulacao(
            simulation_id
        )

        if simulacao is None:
            raise ValueError("Simulação não encontrada.")

        if simulacao["simulation_type"] == "sum_values":
            kind = "neutral"

        return self.repository.criar_item(
            simulation_id=simulation_id,
            title=title,
            kind=kind,
            item_date=item_date,
            amount_cents=amount_cents,
            sort_order=sort_order,
            notes=notes,
        )

    def excluir_item(
            self,
            item_id: int,
    ) -> None:

        self.repository.excluir_item(
            item_id
        )

    def calcular_resumo(
            self,
            simulation_type: str,
            items: list[dict],
    ) -> dict:

        if simulation_type == "sum_values":
            total_cents = sum(
                int(item["amount_cents"] or 0)
                for item in items
            )

            return {
                "total_cents": total_cents,
                "income_cents": 0,
                "expense_cents": 0,
                "balance_cents": total_cents,
            }

        income_cents = sum(
            int(item["amount_cents"] or 0)
            for item in items
            if item["kind"] == "income"
        )

        expense_cents = sum(
            int(item["amount_cents"] or 0)
            for item in items
            if item["kind"] == "expense"
        )

        return {
            "total_cents": income_cents - expense_cents,
            "income_cents": income_cents,
            "expense_cents": expense_cents,
            "balance_cents": income_cents - expense_cents,
        }

    def montar_eventos_timeline(
            self,
            simulation: dict,
    ) -> list[dict]:

        eventos = []

        for item in simulation.get("items", []):
            eventos.append(
                {
                    "id": item["id"],
                    "date": item.get("item_date"),
                    "description": item["title"],
                    "kind": item["kind"],
                    "amount_cents": item["amount_cents"],
                    "status": "simulated",
                }
            )

        return eventos

    def _validar_simulation_type(
            self,
            simulation_type: str,
    ) -> None:

        if simulation_type not in self.VALID_SIMULATION_TYPES:
            raise ValueError(
                f"Tipo de simulação inválido: {simulation_type}"
            )

    def _validar_period_mode(
            self,
            period_mode: str,
    ) -> None:

        if period_mode not in self.VALID_PERIOD_MODES:
            raise ValueError(
                f"Modo de período inválido: {period_mode}"
            )

    def _validar_item_kind(
            self,
            kind: str,
    ) -> None:

        if kind not in self.VALID_ITEM_KINDS:
            raise ValueError(
                f"Tipo de item inválido: {kind}"
            )