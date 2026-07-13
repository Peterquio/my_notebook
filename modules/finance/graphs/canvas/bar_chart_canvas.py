from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QToolTip

from modules.finance.graphs.canvas.base_graph_canvas import (
    BaseGraphCanvas,
)

from modules.finance.graphs.canvas.graph_slice import (
    GraphSlice,
)


class BarChartCanvas(BaseGraphCanvas):
    TOP_MARGIN = 44.0
    BOTTOM_MARGIN = 62.0
    LEFT_MARGIN = 24.0
    RIGHT_MARGIN = 24.0

    BAR_GAP = 14.0
    MIN_BAR_WIDTH = 18.0
    MAX_BAR_WIDTH = 72.0

    VALUE_LABEL_HEIGHT = 24.0
    CATEGORY_LABEL_HEIGHT = 38.0

    def __init__(
            self,
            parent=None,
    ) -> None:

        super().__init__(parent)

        self._bar_paths: list[QPainterPath] = []
        self._visible_items: list[GraphSlice] = []

        self._interactive_hover = True

        self.setMinimumSize(
            320,
            260,
        )

    def set_data(
            self,
            data: list[GraphSlice],
    ) -> None:

        super().set_data(data)

        self._bar_paths.clear()
        self._visible_items.clear()
        self._hover_index = -1

        self.update()

    def set_interactive_hover(
            self,
            enabled: bool,
    ) -> None:

        self._interactive_hover = enabled

        if not enabled:
            self._hover_index = -1
            QToolTip.hideText()

        self.update()

    def paintEvent(
            self,
            event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        painter.setRenderHint(
            QPainter.TextAntialiasing,
            True,
        )

        self._bar_paths = []

        self._visible_items = [
            item
            for item in self.data
            if int(item.value or 0) > 0
        ]

        if not self._visible_items:
            self._desenhar_estado_vazio(
                painter
            )
            return

        max_value = max(
            int(item.value)
            for item in self._visible_items
        )

        if max_value <= 0:
            self._desenhar_estado_vazio(
                painter
            )
            return

        chart_rect = self._obter_chart_rect()

        self._desenhar_linhas_guia(
            painter=painter,
            chart_rect=chart_rect,
            max_value=max_value,
        )

        bar_width = self._calcular_largura_barra(
            chart_rect=chart_rect,
            items_count=len(self._visible_items),
        )

        total_width = (
            bar_width * len(self._visible_items)
            + self.BAR_GAP * (
                len(self._visible_items) - 1
            )
        )

        start_x = (
            chart_rect.center().x()
            - total_width / 2
        )

        for index, item in enumerate(
                self._visible_items
        ):
            x = (
                start_x
                + index * (
                    bar_width
                    + self.BAR_GAP
                )
            )

            value = int(
                item.value
            )

            height_ratio = (
                value
                / max_value
            )

            bar_height = (
                chart_rect.height()
                * height_ratio
            )

            bar_rect = QRectF(
                x,
                chart_rect.bottom() - bar_height,
                bar_width,
                bar_height,
            )

            path = self._criar_barra(
                bar_rect
            )

            self._bar_paths.append(
                path
            )

            self._desenhar_barra(
                painter=painter,
                path=path,
                item=item,
                hovered=(
                    self._interactive_hover
                    and index == self._hover_index
                ),
            )

            self._desenhar_valor_barra(
                painter=painter,
                bar_rect=bar_rect,
                value=value,
            )

            self._desenhar_rotulo_categoria(
                painter=painter,
                bar_rect=bar_rect,
                item=item,
            )

    def _obter_chart_rect(
            self,
    ) -> QRectF:

        left = self.LEFT_MARGIN
        top = self.TOP_MARGIN

        width = max(
            0.0,
            self.width()
            - self.LEFT_MARGIN
            - self.RIGHT_MARGIN,
        )

        height = max(
            0.0,
            self.height()
            - self.TOP_MARGIN
            - self.BOTTOM_MARGIN,
        )

        return QRectF(
            left,
            top,
            width,
            height,
        )

    def _calcular_largura_barra(
            self,
            chart_rect: QRectF,
            items_count: int,
    ) -> float:

        if items_count <= 0:
            return self.MIN_BAR_WIDTH

        available_width = (
            chart_rect.width()
            - self.BAR_GAP
            * max(
                0,
                items_count - 1,
            )
        )

        raw_width = (
            available_width
            / items_count
        )

        return max(
            self.MIN_BAR_WIDTH,
            min(
                self.MAX_BAR_WIDTH,
                raw_width,
            ),
        )

    def _criar_barra(
            self,
            rect: QRectF,
    ) -> QPainterPath:

        radius = min(
            8.0,
            rect.width() / 2,
        )

        path = QPainterPath()

        path.addRoundedRect(
            rect,
            radius,
            radius,
        )

        return path

    def _desenhar_barra(
            self,
            painter: QPainter,
            path: QPainterPath,
            item: GraphSlice,
            hovered: bool,
    ) -> None:

        color = QColor(
            item.color
        )

        if not color.isValid():
            color = QColor(
                "#94A3B8"
            )

        is_uncategorized = bool(
            item.metadata.get(
                "is_uncategorized",
                False,
            )
        )

        if hovered:
            color = color.lighter(
                112
            )

        if is_uncategorized:
            painter.setBrush(
                QBrush(
                    color,
                    Qt.BDiagPattern,
                )
            )
        else:
            painter.setBrush(
                QBrush(
                    color
                )
            )

        painter.setPen(
            QPen(
                QColor(
                    "#FFFFFF"
                ),
                1.5,
            )
        )

        painter.drawPath(
            path
        )

    def _desenhar_valor_barra(
            self,
            painter: QPainter,
            bar_rect: QRectF,
            value: int,
    ) -> None:

        font = QFont(
            self.font()
        )

        font.setPointSize(
            8
        )

        font.setBold(
            True
        )

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(
                "#0F172A"
            )
        )

        value_rect = QRectF(
            bar_rect.left() - 20,
            bar_rect.top()
            - self.VALUE_LABEL_HEIGHT,
            bar_rect.width() + 40,
            self.VALUE_LABEL_HEIGHT,
        )

        painter.drawText(
            value_rect,
            Qt.AlignCenter,
            self._formatar_moeda_compacta(
                value
            ),
        )

    def _desenhar_rotulo_categoria(
            self,
            painter: QPainter,
            bar_rect: QRectF,
            item: GraphSlice,
    ) -> None:

        font = QFont(
            self.font()
        )

        font.setPointSize(
            8
        )

        painter.setFont(
            font
        )

        painter.setPen(
            QColor(
                "#475569"
            )
        )

        label_rect = QRectF(
            bar_rect.left() - 24,
            bar_rect.bottom() + 6,
            bar_rect.width() + 48,
            self.CATEGORY_LABEL_HEIGHT,
        )

        painter.drawText(
            label_rect,
            Qt.AlignHCenter
            | Qt.AlignTop
            | Qt.TextWordWrap,
            item.label,
        )

    def _desenhar_linhas_guia(
            self,
            painter: QPainter,
            chart_rect: QRectF,
            max_value: int,
    ) -> None:

        painter.save()

        pen = QPen(
            QColor(
                148,
                163,
                184,
                48,
            ),
            1,
        )

        pen.setStyle(
            Qt.DashLine
        )

        painter.setPen(
            pen
        )

        painter.setBrush(
            Qt.NoBrush
        )

        steps = 4

        for step in range(
                1,
                steps + 1,
        ):
            ratio = (
                step
                / steps
            )

            y = (
                chart_rect.bottom()
                - chart_rect.height()
                * ratio
            )

            painter.drawLine(
                QPointF(
                    chart_rect.left(),
                    y,
                ),
                QPointF(
                    chart_rect.right(),
                    y,
                ),
            )

        painter.restore()

    def _desenhar_estado_vazio(
            self,
            painter: QPainter,
    ) -> None:

        painter.setPen(
            QColor(
                "#94A3B8"
            )
        )

        font = QFont(
            self.font()
        )

        font.setPointSize(
            11
        )

        painter.setFont(
            font
        )

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            "Nenhum gasto no período",
        )

    def mouseMoveEvent(
            self,
            event: QMouseEvent,
    ) -> None:

        if not self._interactive_hover:
            super().mouseMoveEvent(
                event
            )
            return

        new_hover_index = (
            self._buscar_barra_na_posicao(
                event.position()
            )
        )

        if new_hover_index != self._hover_index:
            self._hover_index = (
                new_hover_index
            )

            self.update()

            if self._hover_index >= 0:
                item = self._visible_items[
                    self._hover_index
                ]

                self.slice_hovered.emit(
                    item
                )

        if self._hover_index >= 0:
            item = self._visible_items[
                self._hover_index
            ]

            self._mostrar_tooltip(
                event=event,
                item=item,
            )

        super().mouseMoveEvent(
            event
        )

    def leaveEvent(
            self,
            event,
    ) -> None:

        if self._hover_index != -1:
            self._hover_index = -1
            self.update()

        QToolTip.hideText()

        super().leaveEvent(
            event
        )

    def mouseReleaseEvent(
            self,
            event: QMouseEvent,
    ) -> None:

        if event.button() == Qt.LeftButton:
            index = self._buscar_barra_na_posicao(
                event.position()
            )

            if 0 <= index < len(
                    self._visible_items
            ):
                self.slice_clicked.emit(
                    self._visible_items[
                        index
                    ]
                )

        super().mouseReleaseEvent(
            event
        )

    def _buscar_barra_na_posicao(
            self,
            position: QPointF,
    ) -> int:

        for index in range(
                len(self._bar_paths) - 1,
                -1,
                -1,
        ):
            if self._bar_paths[index].contains(
                    position
            ):
                return index

        return -1

    def _mostrar_tooltip(
            self,
            event: QMouseEvent,
            item: GraphSlice,
    ) -> None:

        total = sum(
            int(current_item.value)
            for current_item in self._visible_items
        )

        percentage = (
            int(item.value)
            / total
            * 100
            if total > 0
            else 0.0
        )

        tooltip = (
            f"<b>{item.label}</b><br>"
            f"{self._formatar_moeda(item.value)}<br>"
            f"{percentage:.1f}%"
        )

        QToolTip.showText(
            event.globalPosition().toPoint(),
            tooltip,
            self,
        )

    def _formatar_moeda(
            self,
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

    def _formatar_moeda_compacta(
            self,
            value_cents: int,
    ) -> str:

        value = (
            value_cents
            / 100
        )

        if abs(value) >= 1_000_000:
            return (
                f"R$ {value / 1_000_000:.1f} mi"
                .replace(".", ",")
            )

        if abs(value) >= 1_000:
            return (
                f"R$ {value / 1_000:.1f} mil"
                .replace(".", ",")
            )

        return (
            f"R$ {value:,.0f}"
            .replace(",", ".")
        )