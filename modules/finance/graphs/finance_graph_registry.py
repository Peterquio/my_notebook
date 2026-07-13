from modules.finance.graphs.base_finance_graph import (
    BaseFinanceGraph,
)

from modules.finance.graphs.expenses_by_category_graph import (
    ExpensesByCategoryGraph,
)


FINANCE_GRAPH_REGISTRY = {
    ExpensesByCategoryGraph.graph_id: (
        ExpensesByCategoryGraph
    ),
}


def criar_grafico_financeiro(
        graph_id: str,
        username: str,
) -> BaseFinanceGraph:

    graph_class = FINANCE_GRAPH_REGISTRY.get(
        graph_id
    )

    if graph_class is None:
        raise ValueError(
            f"Gráfico financeiro não registrado: {graph_id}"
        )

    return graph_class(
        username=username
    )


def listar_graficos_financeiros() -> list[dict]:
    graficos = []

    for graph_id, graph_class in (
            FINANCE_GRAPH_REGISTRY.items()
    ):
        graficos.append(
            {
                "id": graph_id,
                "title": graph_class.title,
            }
        )

    return graficos