from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QFrame
from ui.widgets.add_card_button import AddCardButton
from core.shared.dashboard.dashboard_layout_engine import DashboardLayoutEngine
from core.shared.dashboard.dashboard_snapshot import DashboardSnapshot

class DashboardGrid(QWidget):
    add_card_requested = Signal()
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

        self.layout_engine = DashboardLayoutEngine(
            min_cell_width=min_cell_width,
            max_cell_width=max_cell_width,
            cell_ratio=cell_ratio,
            spacing=spacing,
        )

        self.items = []
        self.occupied_cells = []
        self.card_positions = {}
        self.snapshot = DashboardSnapshot()
        self.current_columns = 1
        self.drop_preview = QFrame(self)
        self.drop_preview.hide()

        self.edit_mode = False

        self.add_card_button = AddCardButton()
        self.add_card_button.hide()

        self.add_card_button.clicked.connect(
            self.add_card_requested.emit
        )

        self.debug_show_cells = False
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

        is_add_button = widget == self.add_card_button

        if not is_add_button and self.add_card_button in self.card_positions:
            del self.card_positions[self.add_card_button]
            self.add_card_button.hide()

        if not is_add_button:
            self.items = [
                item
                for item in self.items
                if item["widget"] != self.add_card_button
            ]

        self.items.append(
            {
                "widget": widget,
                "size": size,
            }
        )

        width_units, height_units = self._parse_size(size)

        if not self.card_positions:
            self.current_columns = self._calculate_columns(
                max(
                    self._get_available_width(),
                    self.min_cell_width,
                )
            )

        self.occupied_cells = []

        for existing_widget, position in self.card_positions.items():
            if existing_widget == self.add_card_button:
                continue

            self._mark_cells_as_occupied(
                position["row"],
                position["column"],
                position["width_units"],
                position["height_units"],
            )

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

        if self.edit_mode:
            add_exists = any(
                item["widget"] == self.add_card_button
                for item in self.items
            )

            if not add_exists:
                self.items.append(
                    {
                        "widget": self.add_card_button,
                        "size": "1x1",
                    }
                )

            add_row, add_column = self._find_add_card_position()

            self.card_positions[self.add_card_button] = {
                "row": add_row,
                "column": add_column,
                "width_units": 1,
                "height_units": 1,
            }

        self._rebuild_grid_from_positions()

    def add_card_at(
            self,
            widget,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        self.items.append(
            {
                "widget": widget,
                "size": f"{width_units}x{height_units}",
            }
        )

        self.card_positions[widget] = {
            "row": row,
            "column": column,
            "width_units": width_units,
            "height_units": height_units,
        }

        self._rebuild_grid_from_positions()

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

        return self.layout_engine.calculate_columns(
            available_width
        )

    def _calculate_cell_width(
            self,
            available_width: int,
            columns: int,
    ) -> int:

        return self.layout_engine.calculate_cell_width(
            available_width,
            columns,
        )

    def _parse_size(self, size: str) -> tuple[int, int]:
        return self.layout_engine.parse_size(size)

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

        for widget, position in list(self.card_positions.items()):

            if widget == self.add_card_button and not self.edit_mode:
                widget.hide()
                continue
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

    def remove_card(
            self,
            widget,
    ) -> None:

        if widget == self.add_card_button:
            return

        self.items = [
            item
            for item in self.items
            if item["widget"] != widget
        ]

        if widget in self.card_positions:
            del self.card_positions[widget]

        widget.hide()
        widget.setParent(None)

        if self.edit_mode and self.add_card_button in self.card_positions:
            row, column = self._find_add_card_position()

            self.card_positions[self.add_card_button] = {
                "row": row,
                "column": column,
                "width_units": 1,
                "height_units": 1,
            }

        self._rebuild_grid_from_positions()

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

        if column + width_units > self.current_columns:
            return

        self._move_card_with_push(
            widget,
            row,
            column,
            width_units,
            height_units,
        )

        if self.edit_mode:
            self._update_add_card_button_position()

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

        for widget, position in list(self.card_positions.items()):

            if widget == self.add_card_button and not self.edit_mode:
                continue
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

    def _move_card_with_push(
            self,
            moved_widget,
            target_row: int,
            target_column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        old_positions = {
            widget: position.copy()
            for widget, position in self.card_positions.items()
        }

        ordered_widgets = sorted(
            old_positions.keys(),
            key=lambda widget: (
                old_positions[widget]["row"],
                old_positions[widget]["column"],
            ),
        )

        self.card_positions = {}
        self.occupied_cells = []

        self.card_positions[moved_widget] = {
            "row": target_row,
            "column": target_column,
            "width_units": width_units,
            "height_units": height_units,
        }

        self._mark_cells_as_occupied(
            target_row,
            target_column,
            width_units,
            height_units,
        )

        for widget in ordered_widgets:
            if widget == moved_widget:
                continue

            if widget == self.add_card_button:
                continue

            old_position = old_positions[widget]

            old_row = old_position["row"]
            old_column = old_position["column"]
            old_width_units = old_position["width_units"]
            old_height_units = old_position["height_units"]

            if self._can_place_card(
                    old_row,
                    old_column,
                    old_width_units,
                    old_height_units,
            ):
                new_row = old_row
                new_column = old_column
            else:
                new_row, new_column = self._find_available_position_from(
                    old_row,
                    old_column,
                    old_width_units,
                    old_height_units,
                )

            self.card_positions[widget] = {
                "row": new_row,
                "column": new_column,
                "width_units": old_width_units,
                "height_units": old_height_units,
            }

            self._mark_cells_as_occupied(
                new_row,
                new_column,
                old_width_units,
                old_height_units,
            )

    def _find_available_position_from(
            self,
            start_row: int,
            start_column: int,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int]:

        row = start_row
        column = start_column

        while True:
            while column < self.current_columns:
                if self._can_place_card(
                        row,
                        column,
                        width_units,
                        height_units,
                ):
                    return row, column

                column += 1

            row += 1
            column = 0

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

    def compact_empty_rows(self) -> None:
        if not self.card_positions:
            return

        occupied_rows = set()

        for position in self.card_positions.values():
            row = position["row"]
            height_units = position["height_units"]

            for r in range(row, row + height_units):
                occupied_rows.add(r)

        ordered_rows = sorted(occupied_rows)

        row_map = {
            old_row: new_row
            for new_row, old_row in enumerate(ordered_rows)
        }

        for position in self.card_positions.values():
            old_row = position["row"]
            position["row"] = row_map[old_row]

        self._rebuild_grid_from_positions()

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

    def _find_add_card_position(self) -> tuple[int, int]:
        if not self.card_positions:
            return 0, 0

        occupied_cells = set()

        for widget, position in self.card_positions.items():
            if widget == self.add_card_button:
                continue

            row = position["row"]
            column = position["column"]
            width_units = position["width_units"]
            height_units = position["height_units"]

            for r in range(row, row + height_units):
                for c in range(column, column + width_units):
                    occupied_cells.add((r, c))

        if not occupied_cells:
            return 0, 0

        last_row = max(
            row
            for row, column in occupied_cells
        )

        occupied_columns_in_last_row = [
            column
            for row, column in occupied_cells
            if row == last_row
        ]

        last_column = max(occupied_columns_in_last_row)

        next_column = last_column + 1

        if next_column < self.current_columns:
            return last_row, next_column

        return last_row + 1, 0

    def get_layout_items(self) -> list[dict]:
        layout_items = []

        for widget, position in self.card_positions.items():
            if widget == self.add_card_button:
                continue

            card_id = getattr(widget, "card_id", None)
            card_type = getattr(widget, "card_type", None)
            card_config = getattr(widget, "card_config", {})

            if not card_id:
                continue

            layout_items.append(
                {
                    "card_id": card_id,
                    "card_type": card_type,
                    "config": card_config,

                    "row": position["row"],
                    "column": position["column"],
                    "width_units": position["width_units"],
                    "height_units": position["height_units"],
                }
            )

        layout_items.sort(
            key=lambda item: (
                item["row"],
                item["column"],
            )
        )

        return layout_items

    def create_layout_snapshot(
            self,
    ) -> None:

        self.snapshot.create(
            items=self.items,
            card_positions=self.card_positions,
            add_button=self.add_card_button,
        )

    def restore_layout_snapshot(
            self,
    ) -> None:

        if not self.snapshot.has_snapshot():
            return

        snapshot_items = self.snapshot.get_items()

        snapshot_widgets = {
            item["widget"]
            for item in snapshot_items
        }

        current_widgets = {
            item["widget"]
            for item in self.items
        }

        widgets_to_remove = (
                current_widgets
                - snapshot_widgets
        )

        for widget in widgets_to_remove:
            widget.hide()
            widget.setParent(None)

        self.items = snapshot_items

        self.card_positions = (
            self.snapshot.get_positions()
        )

        self.snapshot.clear()

        self.add_card_button.hide()

        self._rebuild_grid_from_positions()

    def _remove_add_card_button(self) -> None:
        self.items = [
            item
            for item in self.items
            if item["widget"] != self.add_card_button
        ]

        if self.add_card_button in self.card_positions:
            del self.card_positions[self.add_card_button]

        self.add_card_button.hide()
        self.add_card_button.setParent(None)

    def _force_hide_add_card_button(self) -> None:
        self.items = [
            item
            for item in self.items
            if item["widget"] != self.add_card_button
        ]

        if self.add_card_button in self.card_positions:
            del self.card_positions[self.add_card_button]

        self.layout.removeWidget(self.add_card_button)
        self.add_card_button.hide()
        self.add_card_button.setParent(None)

    def _update_add_card_button_position(self) -> None:
        if not self.edit_mode:
            return

        if self.add_card_button not in self.items:
            self.items.append(
                {
                    "widget": self.add_card_button,
                    "size": "1x1",
                }
            )

        row, column = self._find_add_card_position()

        self.card_positions[self.add_card_button] = {
            "row": row,
            "column": column,
            "width_units": 1,
            "height_units": 1,
        }

    def set_edit_mode(
            self,
            enabled: bool,
    ) -> None:

        self.edit_mode = enabled

        if enabled:
            existing = any(
                item["widget"] == self.add_card_button
                for item in self.items
            )

            if not existing:
                self.items.append(
                    {
                        "widget": self.add_card_button,
                        "size": "1x1",
                    }
                )

            self._update_add_card_button_position()

            self.add_card_button.setParent(self)
            self.add_card_button.show()

        else:
            self._force_hide_add_card_button()

        self._rebuild_grid_from_positions()

        if not enabled:
            self._force_hide_add_card_button()

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

        minimum_height = self.layout_engine.calculate_minimum_height(
            total_rows=total_rows,
            cell_height=self._last_cell_height,
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

        return self.layout_engine.get_grid_geometry(
            row=row,
            column=column,
            width_units=width_units,
            height_units=height_units,
            cell_width=self._last_cell_width,
            cell_height=self._last_cell_height,
        )

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

