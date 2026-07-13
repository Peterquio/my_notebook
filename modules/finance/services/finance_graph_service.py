from datetime import date

from dateutil.relativedelta import relativedelta

from modules.finance.graphs.finance_graph_registry import (
    criar_grafico_financeiro,
    listar_graficos_financeiros,
)

from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)


class FinanceGraphService:
    DEFAULT_GRAPH_ID = "expenses_by_category"

    VALID_VISUALIZATIONS = {
        "pie",
        "bar",
    }

    def __init__(
            self,
            username: str,
    ) -> None:

        self.username = username

        self.settings_repository = (
            FinanceSettingsRepository(
                username
            )
        )

    def listar_graficos(self) -> list[dict]:
        return listar_graficos_financeiros()

    def obter_configuracao_padrao(
            self,
            reference_date: date | None = None,
    ) -> dict:

        data_referencia = (
            reference_date
            or date.today()
        )

        inicio, _ = self.calcular_periodo(
            selected_year=data_referencia.year,
            selected_month=data_referencia.month,
        )

        inicio_data = date.fromisoformat(
            inicio
        )

        if data_referencia < inicio_data:
            inicio_data = (
                inicio_data
                + relativedelta(months=-1)
            )

        return {
            "graph_id": self.DEFAULT_GRAPH_ID,
            "visualization": "pie",
            "selected_year": inicio_data.year,
            "selected_month": inicio_data.month,
        }

    def normalizar_configuracao(
            self,
            config: dict | None,
    ) -> dict:

        padrao = self.obter_configuracao_padrao()

        config_normalizada = {
            **padrao,
            **(config or {}),
        }

        graph_id = config_normalizada.get(
            "graph_id"
        )

        graph_ids_validos = {
            graph["id"]
            for graph in self.listar_graficos()
        }

        if graph_id not in graph_ids_validos:
            config_normalizada["graph_id"] = (
                self.DEFAULT_GRAPH_ID
            )

        visualization = config_normalizada.get(
            "visualization"
        )

        if visualization not in self.VALID_VISUALIZATIONS:
            config_normalizada["visualization"] = "pie"

        selected_year = int(
            config_normalizada["selected_year"]
        )

        selected_month = int(
            config_normalizada["selected_month"]
        )

        if not 1 <= selected_month <= 12:
            raise ValueError(
                "Mês selecionado inválido."
            )

        if selected_year < 2000:
            raise ValueError(
                "Ano selecionado inválido."
            )

        config_normalizada["selected_year"] = (
            selected_year
        )

        config_normalizada["selected_month"] = (
            selected_month
        )

        return config_normalizada

    def carregar_grafico(
            self,
            config: dict | None = None,
    ) -> dict:

        config_normalizada = (
            self.normalizar_configuracao(
                config
            )
        )

        start_date, end_date = (
            self.calcular_periodo(
                selected_year=config_normalizada[
                    "selected_year"
                ],
                selected_month=config_normalizada[
                    "selected_month"
                ],
            )
        )

        graph = criar_grafico_financeiro(
            graph_id=config_normalizada["graph_id"],
            username=self.username,
        )

        dados = graph.carregar_dados(
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "config": config_normalizada,
            "data": dados,
        }

    def calcular_periodo(
            self,
            selected_year: int,
            selected_month: int,
    ) -> tuple[str, str]:

        reference_day = (
            self.settings_repository
            .obter_reference_day()
        )

        primeiro_dia_mes = date(
            selected_year,
            selected_month,
            1,
        )

        ultimo_dia_mes = (
            primeiro_dia_mes
            + relativedelta(day=31)
        ).day

        dia_inicio = min(
            reference_day,
            ultimo_dia_mes,
        )

        start_date = date(
            selected_year,
            selected_month,
            dia_inicio,
        )

        proximo_mes = (
            start_date
            + relativedelta(months=1)
        )

        end_date = (
            proximo_mes
            + relativedelta(days=-1)
        )

        return (
            start_date.isoformat(),
            end_date.isoformat(),
        )