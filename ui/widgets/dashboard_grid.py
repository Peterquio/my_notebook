from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QFrame

class DashboardGrid(QWidget):
    def __init__(
        self,
        min_cell_width: int = 240,
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
        self.card_positions = {}
        self.current_columns = 1
        self.drop_preview = QFrame(self)
        self.drop_preview.hide()

        self.debug_show_cells = True
        self.debug_cell_frames = []

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

        self.card_positions = {}

        self._last_cell_width = self.min_cell_width
        self._last_cell_height = int(self.min_cell_width * self.cell_ratio)
        self.extra_drop_rows = 1

        self._drag_auto_scroll_active = False
        self._auto_scroll_direction = 0
        self._auto_scroll_speed = 18
        self._auto_scroll_margin = 80

        self._auto_scroll_timer = QTimer(self)
        self._auto_scroll_timer.setInterval(30)
        self._auto_scroll_timer.timeout.connect(self._perform_auto_scroll)

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
        if self.card_positions:
            self._rebuild_grid_from_positions()
        else:
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
        self._last_cell_width = cell_width
        self._last_cell_height = cell_height

        self._apply_fixed_grid_tracks(
            cell_width,
            cell_height,
        )

        for item in self.items:
            widget = item["widget"]
            size = item["size"]

            width_units, height_units = self._parse_size(size)

            row, column = self._find_available_position(
                width_units,
                height_units,
            )

            self._apply_widget_span_size(
                widget,
                width_units,
                height_units,
            )

            self._place_widget_on_grid(
                widget,
                row,
                column,
                width_units,
                height_units,
            )

            self.card_positions[widget] = {
                "row": row,
                "column": column,
                "width_units": width_units,
                "height_units": height_units,
            }

            self._mark_cells_as_occupied(
                row,
                column,
                width_units,
                height_units,
            )

        self._update_minimum_grid_height()

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

        return min(6, max(3, columns))

    def _calculate_cell_width(
            self,
            available_width: int,
            columns: int,
    ) -> int:

        return self.min_cell_width

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

    def get_cards_in_area(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> list:

        target_cells = set()

        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                target_cells.add((r, c))

        conflicting_cards = []

        for widget, position in self.card_positions.items():
            widget_cells = set()

            widget_row = position["row"]
            widget_column = position["column"]
            widget_width = position["width_units"]
            widget_height = position["height_units"]

            for r in range(widget_row, widget_row + widget_height):
                for c in range(widget_column, widget_column + widget_width):
                    widget_cells.add((r, c))

            if target_cells.intersection(widget_cells):
                conflicting_cards.append(widget)

        return conflicting_cards

    def can_drop_card_at(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> bool:

        if column + width_units > self.current_columns:
            return False

        return True

    def _clear_layout(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)

            if item.widget():
                self.layout.removeWidget(item.widget())

    def get_cell_from_global_position(
            self,
            global_pos,
    ) -> tuple[int, int] | None:

        local_pos = self.mapFromGlobal(global_pos)

        if not self.rect().contains(local_pos):
            return None

        used_rows = max(
            (
                position["row"] + position["height_units"]
                for position in self.card_positions.values()
            ),
            default=0,
        )

        total_rows = used_rows + self.extra_drop_rows

        for row in range(total_rows):
            for column in range(self.current_columns):
                cell_rect = self.layout.cellRect(
                    row,
                    column,
                )

                if cell_rect.contains(local_pos):
                    return row, column

        return None

    def show_drop_preview(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
            valid: bool,
    ) -> None:

        x, y, width, height = self._get_grid_geometry(
            row,
            column,
            width_units,
            height_units,
        )

        if valid:
            color = "rgba(34, 197, 94, 55)"
            border = "rgba(34, 197, 94, 150)"
        else:
            color = "rgba(239, 68, 68, 45)"
            border = "rgba(239, 68, 68, 140)"

        self.drop_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px dashed {border};
                border-radius: 18px;
            }}
        """)

        self.drop_preview.setGeometry(
            x,
            y,
            width,
            height,
        )

        self.drop_preview.show()
        self.drop_preview.raise_()

    def hide_drop_preview(self) -> None:
        self.drop_preview.hide()
        self._stop_auto_scroll()

    def move_card_to(
            self,
            widget,
            row: int,
            column: int,
    ) -> None:

        if widget not in self.card_positions:
            return

        position = self.card_positions[widget]

        width_units = position["width_units"]
        height_units = position["height_units"]

        self.layout.removeWidget(widget)

        self.card_positions[widget] = {
            "row": row,
            "column": column,
            "width_units": width_units,
            "height_units": height_units,
        }

        self._rebuild_grid_from_positions()

    def _rebuild_grid_from_positions(self) -> None:
        self._clear_layout()
        self.occupied_cells = []

        available_width = max(
            self._get_available_width(),
            self.min_cell_width,
        )

        old_columns = self.current_columns

        self.current_columns = self._calculate_columns(
            available_width
        )

        if (
                self.current_columns < old_columns
                and self._has_cards_outside_current_columns()
        ):
            self._reflow_cards_after_column_reduction()

        cell_width = self._calculate_cell_width(
            available_width,
            self.current_columns,
        )

        cell_height = int(cell_width * self.cell_ratio)

        self._last_cell_width = cell_width
        self._last_cell_height = cell_height

        self._apply_fixed_grid_tracks(
            cell_width,
            cell_height,
        )

        for widget, position in self.card_positions.items():
            row = position["row"]
            column = position["column"]
            width_units = position["width_units"]
            height_units = position["height_units"]

            self._apply_widget_span_size(
                widget,
                width_units,
                height_units,
            )

            self._place_widget_on_grid(
                widget,
                row,
                column,
                width_units,
                height_units,
            )

            self._mark_cells_as_occupied(
                row,
                column,
                width_units,
                height_units,
            )

        self._update_minimum_grid_height()
        self._update_debug_cells()

    def compact_empty_rows(self) -> None:
        used_rows = sorted({
            position["row"]
            for position in self.card_positions.values()
        })

        row_map = {
            old_row: new_row
            for new_row, old_row in enumerate(used_rows)
        }

        for position in self.card_positions.values():
            position["row"] = row_map[position["row"]]

        self._rebuild_grid_from_positions()

    def _apply_widget_span_size(
            self,
            widget,
            width_units: int,
            height_units: int,
    ) -> None:

        real_width = (
                self._last_cell_width * width_units
                + self.spacing * (width_units - 1)
        )

        real_height = (
                self._last_cell_height * height_units
                + self.spacing * (height_units - 1)
        )

        if hasattr(widget, "set_base_size"):
            scale = getattr(widget, "scale", 1)

            widget.set_base_size(
                int(real_width / scale),
                int(real_height / scale),
            )
        else:
            widget.setFixedSize(
                real_width,
                real_height,
            )

    def _has_cards_outside_current_columns(self) -> bool:
        for position in self.card_positions.values():
            column = position["column"]
            width_units = position["width_units"]

            last_occupied_column = column + width_units - 1

            if last_occupied_column >= self.current_columns:
                return True

        return False

    def _reflow_cards_after_column_reduction(self) -> None:
        ordered_cards = sorted(
            self.card_positions.items(),
            key=lambda item: (
                item[1]["row"],
                item[1]["column"],
            ),
        )

        self.occupied_cells = []

        for widget, position in ordered_cards:
            width_units = position["width_units"]
            height_units = position["height_units"]

            if width_units > self.current_columns:
                width_units = self.current_columns

            row, column = self._find_available_position(
                width_units,
                height_units,
            )

            self.card_positions[widget] = {
                "row": row,
                "column": column,
                "width_units": width_units,
                "height_units": height_units,
            }

            self._mark_cells_as_occupied(
                row,
                column,
                width_units,
                height_units,
            )

    def start_drag_auto_scroll(self) -> None:
        self._drag_auto_scroll_active = True

    def stop_drag_auto_scroll(self) -> None:
        self._drag_auto_scroll_active = False
        self._stop_auto_scroll()

    def update_drag_auto_scroll(self, global_pos) -> None:
        if not self._drag_auto_scroll_active:
            self._stop_auto_scroll()
            return

        scroll_area = self._get_scroll_area_parent()

        if scroll_area is None:
            self._stop_auto_scroll()
            return

        viewport_pos = scroll_area.viewport().mapFromGlobal(global_pos)
        viewport_height = scroll_area.viewport().height()

        if viewport_pos.y() < self._auto_scroll_margin:
            self._auto_scroll_direction = -1
        elif viewport_pos.y() > viewport_height - self._auto_scroll_margin:
            self._auto_scroll_direction = 1
        else:
            self._stop_auto_scroll()
            return

        if not self._auto_scroll_timer.isActive():
            self._auto_scroll_timer.start()

    def _perform_auto_scroll(self) -> None:
        scroll_area = self._get_scroll_area_parent()

        if scroll_area is None:
            self._stop_auto_scroll()
            return

        scroll_bar = scroll_area.verticalScrollBar()

        scroll_bar.setValue(
            scroll_bar.value()
            + self._auto_scroll_direction * self._auto_scroll_speed
        )

    def _stop_auto_scroll(self) -> None:
        self._auto_scroll_direction = 0

        if self._auto_scroll_timer.isActive():
            self._auto_scroll_timer.stop()

    def _get_scroll_area_parent(self) -> QScrollArea | None:
        parent = self.parentWidget()

        while parent is not None:
            if isinstance(parent, QScrollArea):
                return parent

            parent = parent.parentWidget()

        return None

    def _update_minimum_grid_height(self) -> None:
        if not self.card_positions:
            return

        used_rows = max(
            position["row"] + position["height_units"]
            for position in self.card_positions.values()
        )

        total_rows = used_rows + self.extra_drop_rows

        minimum_height = (
                total_rows * self._last_cell_height
                + max(0, total_rows - 1) * self.spacing
        )

        self.setMinimumHeight(minimum_height)

    def _apply_fixed_grid_tracks(
            self,
            cell_width: int,
            cell_height: int,
    ) -> None:

        self._clear_unused_grid_tracks()

        for column in range(self.current_columns):
            self.layout.setColumnMinimumWidth(
                column,
                cell_width,
            )

            self.layout.setColumnStretch(
                column,
                0,
            )

        # Coluna fantasma: absorve a sobra horizontal da tela.
        # Assim, o espaço ENTRE as colunas reais não aumenta.
        spacer_column = self.current_columns

        self.layout.setColumnMinimumWidth(
            spacer_column,
            0,
        )

        self.layout.setColumnStretch(
            spacer_column,
            1,
        )

        max_row = 0

        for position in self.card_positions.values():
            max_row = max(
                max_row,
                position["row"] + position["height_units"],
            )

        total_rows = max_row + getattr(self, "extra_drop_rows", 0)

        for row in range(total_rows):
            self.layout.setRowMinimumHeight(
                row,
                cell_height,
            )

            self.layout.setRowStretch(
                row,
                0,
            )

    def _clear_unused_grid_tracks(self) -> None:
        for row in range(100):
            self.layout.setRowMinimumHeight(row, 0)
            self.layout.setRowStretch(row, 0)

        for column in range(20):
            self.layout.setColumnMinimumWidth(column, 0)
            self.layout.setColumnStretch(column, 0)

    def _update_debug_cells(self) -> None:
        for frame in self.debug_cell_frames:
            frame.deleteLater()

        self.debug_cell_frames = []

        if not self.debug_show_cells:
            return

        used_rows = max(
            (
                position["row"] + position["height_units"]
                for position in self.card_positions.values()
            ),
            default=0,
        )

        total_rows = used_rows + self.extra_drop_rows

        for row in range(total_rows):
            for column in range(self.current_columns):
                x, y, width, height = self._get_grid_geometry(
                    row,
                    column,
                    1,
                    1,
                )

                frame = QFrame(self)
                frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(59, 130, 246, 25);
                        border: 1px solid rgba(59, 130, 246, 90);
                    }
                """)

                frame.setGeometry(
                    x,
                    y,
                    width,
                    height,
                )
                frame.lower()
                frame.show()

                self.debug_cell_frames.append(frame)

    def _get_grid_geometry(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int, int, int]:

        x = column * (self._last_cell_width + self.spacing)
        y = row * (self._last_cell_height + self.spacing)

        width = (
                self._last_cell_width * width_units
                + self.spacing * (width_units - 1)
        )

        height = (
                self._last_cell_height * height_units
                + self.spacing * (height_units - 1)
        )

        return x, y, width, height

    def _place_widget_on_grid(
            self,
            widget,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        self._apply_widget_span_size(
            widget,
            width_units,
            height_units,
        )

        x, y, width, height = self._get_grid_geometry(
            row,
            column,
            width_units,
            height_units,
        )

        widget.setParent(self)
        widget.setGeometry(x, y, width, height)
        widget.show()
        widget.raise_()

