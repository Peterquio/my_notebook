from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea

class DashboardGrid(QWidget):
    def __init__(
        self,
        min_cell_width: int = 220,
        max_cell_width: int = 300,
        cell_ratio: float = 0.70,
        spacing: int = 20,
    ):
        super().__init__()

        self.min_cell_width = min_cell_width
        self.max_cell_width = max_cell_width
        self.cell_ratio = cell_ratio
        self.spacing = spacing

        self.items = []
        self.occupied_cells = []
        self.current_columns = 1

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

    def add_card(
        self,
        widget,
        size: str = "1x1",
    ) -> None:
        self.items.append(
            {
                "widget": widget,
                "size": size,
            }
        )

        self._rebuild_grid()

    def resizeEvent(self, event) -> None:
        self._rebuild_grid()
        super().resizeEvent(event)

    def _rebuild_grid(self) -> None:
        if not self.items:
            return

        self._clear_layout()
        self.occupied_cells = []

        parent_width = self.parentWidget().width() if self.parentWidget() else self.width()

        available_width = max(
            self._get_available_width(),
            self.min_cell_width,
        )

        self.current_columns = self._calculate_columns(
            available_width
        )

        cell_width = self._calculate_cell_width(
            available_width,
            self.current_columns,
        )

        cell_height = int(cell_width * self.cell_ratio)

        for item in self.items:
            widget = item["widget"]
            size = item["size"]

            width_units, height_units = self._parse_size(size)

            row, column = self._find_available_position(
                width_units,
                height_units,
            )

            real_width = (
                cell_width * width_units
                + self.spacing * (width_units - 1)
            )

            real_height = (
                cell_height * height_units
                + self.spacing * (height_units - 1)
            )

            if hasattr(widget, "set_base_size"):
                scale = getattr(widget, "scale", 1)

                widget.set_base_size(
                    int(real_width / scale),
                    int(real_height / scale),
                )

            self.layout.addWidget(
                widget,
                row,
                column,
                height_units,
                width_units,
            )

            self._mark_cells_as_occupied(
                row,
                column,
                width_units,
                height_units,
            )

    def _get_available_width(self) -> int:
        parent = self.parentWidget()

        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent.viewport().width()

            parent = parent.parentWidget()

        return self.width()

    def _calculate_columns(
            self,
            available_width: int,
    ) -> int:

        minimum_column_width = (
                self.min_cell_width
                + self.spacing
        )

        columns = available_width // minimum_column_width

        return max(3, columns)

    def _calculate_cell_width(
            self,
            available_width: int,
            columns: int,
    ) -> int:
        total_spacing = self.spacing * (columns - 1)

        cell_width = (
                             available_width - total_spacing
                     ) // columns

        return min(
            self.max_cell_width,
            max(self.min_cell_width, cell_width),
        )

    def _parse_size(self, size: str) -> tuple[int, int]:
        width, height = size.lower().split("x")

        return int(width), int(height)

    def _find_available_position(
        self,
        width_units: int,
        height_units: int,
    ) -> tuple[int, int]:
        row = 0

        while True:
            for column in range(self.current_columns):
                if self._can_place_card(
                    row,
                    column,
                    width_units,
                    height_units,
                ):
                    return row, column

            row += 1

    def _can_place_card(
        self,
        row: int,
        column: int,
        width_units: int,
        height_units: int,
    ) -> bool:
        if column + width_units > self.current_columns:
            return False

        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                if (r, c) in self.occupied_cells:
                    return False

        return True

    def _mark_cells_as_occupied(
        self,
        row: int,
        column: int,
        width_units: int,
        height_units: int,
    ) -> None:
        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                self.occupied_cells.append((r, c))

    def _clear_layout(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)

            if item.widget():
                self.layout.removeWidget(item.widget())