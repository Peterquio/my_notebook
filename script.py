import sys
from datetime import date

from dateutil.relativedelta import relativedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from modules.finance.graphs.canvas.bar_chart_canvas import (
    BarChartCanvas,
)

from modules.finance.graphs.canvas.graph_slice import (
    GraphSlice,
)

from modules.finance.services.finance_graph_service import (
    FinanceGraphService,
)


USERNAME = "default"


def formatar_moeda(
        value_cents: int,
) -> str:

    value = (
        value_cents
        / 100
    )

    return (
        f"R$ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_data(
        data_iso: str,
) -> str:

    ano, mes, dia = data_iso.split("-")

    return f"{dia}/{mes}/{ano}"


def criar_graph_slices(
        categories: list[dict],
) -> list[GraphSlice]:

    slices = []

    for category in categories:
        value = int(
            category.get("amount_cents")
            or 0
        )

        if value <= 0:
            continue

        slices.append(
            GraphSlice(
                label=category.get(
                    "name",
                    "Sem categoria",
                ),
                value=value,
                color=category.get(
                    "color",
                    "#94A3B8",
                ),
                metadata={
                    "category_id": category.get(
                        "category_id"
                    ),
                    "items_count": category.get(
                        "items_count",
                        0,
                    ),
                    "items": category.get(
                        "items",
                        [],
                    ),
                    "is_uncategorized": category.get(
                        "is_uncategorized",
                        False,
                    ),
                },
            )
        )

    return slices


class GraphTestWindow(QMainWindow):
    def __init__(
            self,
            title: str,
            result: dict,
            parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.result = result
        self.graph_data = result["data"]

        self.setWindowTitle(
            title
        )

        self.resize(
            1100,
            680,
        )

        self._criar_interface()

    def _criar_interface(
            self,
    ) -> None:

        central_widget = QWidget()

        layout = QVBoxLayout(
            central_widget
        )

        layout.setContentsMargins(
            24,
            20,
            24,
            24,
        )

        layout.setSpacing(
            10
        )

        periodo_label = QLabel(
            (
                f"{formatar_data(self.graph_data['start_date'])}"
                f" até "
                f"{formatar_data(self.graph_data['end_date'])}"
            )
        )

        periodo_label.setAlignment(
            Qt.AlignCenter
        )

        periodo_label.setStyleSheet(
            """
            QLabel {
                color: #475569;
                font-size: 14px;
                font-weight: 600;
            }
            """
        )

        resumo_label = QLabel(
            (
                f"Entradas: "
                f"{formatar_moeda(self.graph_data['income_cents'])}"
                f"    |    "
                f"Gastos: "
                f"{formatar_moeda(self.graph_data['expense_cents'])}"
            )
        )

        resumo_label.setAlignment(
            Qt.AlignCenter
        )

        resumo_label.setStyleSheet(
            """
            QLabel {
                color: #0f172a;
                font-size: 17px;
                font-weight: 700;
                padding-bottom: 8px;
            }
            """
        )

        self.canvas = BarChartCanvas()

        self.canvas.set_data(
            criar_graph_slices(
                self.graph_data["categories"]
            )
        )

        self.canvas.slice_clicked.connect(
            self._mostrar_categoria_clicada
        )

        layout.addWidget(
            periodo_label
        )

        layout.addWidget(
            resumo_label
        )

        layout.addWidget(
            self.canvas,
            1,
        )

        self.setCentralWidget(
            central_widget
        )

    def _mostrar_categoria_clicada(
            self,
            graph_slice: GraphSlice,
    ) -> None:

        print()
        print("=" * 80)
        print(
            f"CATEGORIA: {graph_slice.label}"
        )
        print("=" * 80)

        print(
            "Total:",
            formatar_moeda(
                graph_slice.value
            ),
        )

        print(
            "Quantidade de itens:",
            graph_slice.metadata.get(
                "items_count",
                0,
            ),
        )

        for item in graph_slice.metadata.get(
                "items",
                [],
        ):
            print(
                "   ",
                item.get("date"),
                "|",
                item.get("description"),
                "|",
                formatar_moeda(
                    int(
                        item.get("amount_cents")
                        or 0
                    )
                ),
                "|",
                item.get("source"),
            )


def obter_competencias_teste(
        service: FinanceGraphService,
) -> tuple[dict, dict]:

    configuracao_atual = (
        service.obter_configuracao_padrao()
    )

    data_competencia_atual = date(
        configuracao_atual["selected_year"],
        configuracao_atual["selected_month"],
        1,
    )

    data_competencia_anterior = (
        data_competencia_atual
        + relativedelta(months=-1)
    )

    configuracao_anterior = {
        "graph_id": "expenses_by_category",
        "visualization": "bar",
        "selected_year": (
            data_competencia_anterior.year
        ),
        "selected_month": (
            data_competencia_anterior.month
        ),
    }

    configuracao_atual = {
        **configuracao_atual,
        "visualization": "bar",
    }

    return (
        configuracao_atual,
        configuracao_anterior,
    )


def main() -> None:
    app = QApplication(
        sys.argv
    )

    service = FinanceGraphService(
        username=USERNAME
    )

    (
        configuracao_atual,
        configuracao_anterior,
    ) = obter_competencias_teste(
        service
    )

    resultado_atual = service.carregar_grafico(
        configuracao_atual
    )

    resultado_anterior = service.carregar_grafico(
        configuracao_anterior
    )

    config_atual = resultado_atual["config"]
    config_anterior = resultado_anterior["config"]

    janela_atual = GraphTestWindow(
        title=(
            "Gráfico real — período atual "
            f"{config_atual['selected_month']:02d}/"
            f"{config_atual['selected_year']}"
        ),
        result=resultado_atual,
    )

    janela_anterior = GraphTestWindow(
        title=(
            "Gráfico real — período anterior "
            f"{config_anterior['selected_month']:02d}/"
            f"{config_anterior['selected_year']}"
        ),
        result=resultado_anterior,
    )

    janela_atual.move(
        80,
        80,
    )

    janela_anterior.move(
        160,
        130,
    )

    janela_atual.show()
    janela_anterior.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()