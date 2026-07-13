from math import cos, radians, sin

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


class PieChartCanvas(BaseGraphCanvas):
    START_ANGLE = 90.0

    INNER_RADIUS_RATIO = 0.58
    HOVER_OFFSET = 5.0

    OUTER_MARGIN = 48.0
    SLICE_GAP_DEGREES = 1.0

    MAX_DIAMETER = 440.0

    def __init__(
            self,
            parent=None,
    ) -> None:

        super().__init__(parent)

        self._slice_paths: list[QPainterPath] = []
        self._interactive_hover = True

        self.setMinimumSize(
            280,
            280,
        )

    def set_data(
            self,
            data: list[GraphSlice],
    ) -> None:

        super().set_data(data)

        self._slice_paths.clear()
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

        self._slice_paths = []

        valid_items = [
            item
            for item in self.data
            if int(item.value or 0) > 0
        ]

        total = sum(
            int(item.value)
            for item in valid_items
        )

        if not valid_items or total <= 0:
            self._desenhar_estado_vazio(
                painter
            )
            return

        chart_rect = self._obter_chart_rect()
        current_angle = self.START_ANGLE

        for index, item in enumerate(valid_items):
            value = int(
                item.value
            )

            full_span = (
                value
                / total
                * 360.0
            )

            gap = min(
                self.SLICE_GAP_DEGREES,
                full_span * 0.15,
            )

            visible_start = (
                current_angle
                - gap / 2
            )

            visible_span = max(
                0.15,
                full_span - gap,
            )

            middle_angle = (
                visible_start
                - visible_span / 2
            )

            offset = (
                self.HOVER_OFFSET
                if (
                        self._interactive_hover
                        and index == self._hover_index
                )
                else 0.0
            )

            offset_point = self._calcular_offset(
                angle=middle_angle,
                distance=offset,
            )

            translated_rect = chart_rect.translated(
                offset_point.x(),
                offset_point.y(),
            )

            path = self._criar_fatia_rosca(
                chart_rect=translated_rect,
                start_angle=visible_start,
                span_angle=visible_span,
            )

            self._slice_paths.append(
                path
            )

            self._desenhar_fatia(
                painter=painter,
                path=path,
                item=item,
                hovered=(
                        self._interactive_hover
                        and index == self._hover_index
                ),
            )

            current_angle -= full_span

        self._desenhar_centro(
            painter=painter,
            chart_rect=chart_rect,
            total=total,
        )

    def _obter_chart_rect(
            self,
    ) -> QRectF:

        available_width = max(
            0.0,
            self.width() - self.OUTER_MARGIN * 2,
        )

        available_height = max(
            0.0,
            self.height() - self.OUTER_MARGIN * 2,
        )

        diameter = min(
            available_width,
            available_height,
            self.MAX_DIAMETER,
        )

        left = (
            self.width() - diameter
        ) / 2

        top = (
            self.height() - diameter
        ) / 2

        return QRectF(
            left,
            top,
            diameter,
            diameter,
        )

    def _criar_fatia_rosca(
            self,
            chart_rect: QRectF,
            start_angle: float,
            span_angle: float,
    ) -> QPainterPath:

        center = chart_rect.center()

        outer_sector = QPainterPath()

        outer_sector.moveTo(
            center
        )

        outer_sector.arcTo(
            chart_rect,
            start_angle,
            -span_angle,
        )

        outer_sector.closeSubpath()

        outer_radius = (
            chart_rect.width()
            / 2
        )

        inner_radius = (
            outer_radius
            * self.INNER_RADIUS_RATIO
        )

        inner_rect = QRectF(
            center.x() - inner_radius,
            center.y() - inner_radius,
            inner_radius * 2,
            inner_radius * 2,
        )

        inner_circle = QPainterPath()

        inner_circle.addEllipse(
            inner_rect
        )

        return outer_sector.subtracted(
            inner_circle
        )

    def _calcular_offset(
            self,
            angle: float,
            distance: float,
    ) -> QPointF:

        angle_rad = radians(
            angle
        )

        return QPointF(
            cos(angle_rad) * distance,
            -sin(angle_rad) * distance,
        )

    def _desenhar_fatia(
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

        if hovered:
            painter.setPen(
                QPen(
                    QColor(
                        "#0F172A"
                    ),
                    2.0,
                )
            )
        else:
            painter.setPen(
                QPen(
                    QColor(
                        "#FFFFFF"
                    ),
                    2.0,
                )
            )

        painter.drawPath(
            path
        )

    def _desenhar_centro(
            self,
            painter: QPainter,
            chart_rect: QRectF,
            total: int,
    ) -> None:

        outer_radius = (
            chart_rect.width()
            / 2
        )

        inner_radius = (
            outer_radius
            * self.INNER_RADIUS_RATIO
        )

        center = chart_rect.center()

        center_rect = QRectF(
            center.x() - inner_radius,
            center.y() - inner_radius,
            inner_radius * 2,
            inner_radius * 2,
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(
                "#FFFFFF"
            )
        )

        painter.drawEllipse(
            center_rect
        )

        label_font = QFont(
            self.font()
        )

        label_font.setPointSize(
            9
        )

        label_font.setWeight(
            QFont.Medium
        )

        painter.setFont(
            label_font
        )

        painter.setPen(
            QColor(
                "#64748B"
            )
        )

        label_rect = QRectF(
            center_rect.left() + 8,
            center_rect.top()
            + center_rect.height() * 0.28,
            center_rect.width() - 16,
            center_rect.height() * 0.18,
        )

        painter.drawText(
            label_rect,
            Qt.AlignCenter,
            "Total de gastos",
        )

        value_font = QFont(
            self.font()
        )

        value_font.setPointSize(
            13
        )

        value_font.setBold(
            True
        )

        painter.setFont(
            value_font
        )

        painter.setPen(
            QColor(
                "#0F172A"
            )
        )

        value_rect = QRectF(
            center_rect.left() + 8,
            center_rect.top()
            + center_rect.height() * 0.46,
            center_rect.width() - 16,
            center_rect.height() * 0.24,
        )

        painter.drawText(
            value_rect,
            Qt.AlignCenter,
            self._formatar_moeda(
                total
            ),
        )

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
            self._buscar_fatia_na_posicao(
                event.position()
            )
        )

        if new_hover_index != self._hover_index:
            self._hover_index = new_hover_index

            self.update()

            if self._hover_index >= 0:
                item = self._obter_item_visivel(
                    self._hover_index
                )

                if item is not None:
                    self.slice_hovered.emit(
                        item
                    )

        if self._hover_index >= 0:
            item = self._obter_item_visivel(
                self._hover_index
            )

            if item is not None:
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
            index = self._buscar_fatia_na_posicao(
                event.position()
            )

            item = self._obter_item_visivel(
                index
            )

            if item is not None:
                self.slice_clicked.emit(
                    item
                )

        super().mouseReleaseEvent(
            event
        )

    def _buscar_fatia_na_posicao(
            self,
            position: QPointF,
    ) -> int:

        for index in range(
                len(self._slice_paths) - 1,
                -1,
                -1,
        ):
            if self._slice_paths[index].contains(
                    position
            ):
                return index

        return -1

    def _obter_item_visivel(
            self,
            visible_index: int,
    ) -> GraphSlice | None:

        if visible_index < 0:
            return None

        visible_items = [
            item
            for item in self.data
            if int(item.value or 0) > 0
        ]

        if visible_index >= len(
                visible_items
        ):
            return None

        return visible_items[
            visible_index
        ]

    def _mostrar_tooltip(
            self,
            event: QMouseEvent,
            item: GraphSlice,
    ) -> None:

        total = sum(
            int(current_item.value)
            for current_item in self.data
            if int(current_item.value or 0) > 0
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