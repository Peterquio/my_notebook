from modules.finance.graphs.canvas.bar_chart_canvas import (
    BarChartCanvas,
)

from modules.finance.graphs.canvas.pie_chart_canvas import (
    PieChartCanvas,
)


class GraphCanvasFactory:
    @staticmethod
    def create(
            chart_type: str,
            parent=None,
    ):

        normalized_type = (
            chart_type
            .strip()
            .lower()
        )

        canvas_classes = {
            "pie": PieChartCanvas,
            "bar": BarChartCanvas,
        }

        canvas_class = canvas_classes.get(
            normalized_type
        )

        if canvas_class is None:
            raise ValueError(
                f"Tipo de gráfico não suportado: {chart_type}"
            )

        return canvas_class(
            parent=parent
        )