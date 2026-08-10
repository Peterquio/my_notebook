from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QScrollArea, QFrame
from ui.widgets.add_card_button import AddCardButton

from core.shared.dashboard.dashboard_layout_engine import DashboardLayoutEngine
from core.shared.dashboard.dashboard_snapshot import DashboardSnapshot
from core.shared.dashboard.dashboard_autoscroll import DashboardAutoScroll
from core.shared.dashboard.dashboard_renderer import DashboardRenderer
from core.shared.dashboard.dashboard_free_position_strategy import FreePositionStrategy
from core.shared.dashboard.dashboard_sequential_strategy import SequentialStrategy
from core.shared.dashboard.dashboard_drag_engine import DashboardDragEngine

class DashboardGrid(QWidget):
    add_card_requested = Signal()
    def __init__(
        self,
        min_cell_width: int = 240,
        max_cell_width: int = 300,
        cell_ratio: float = 0.70,
        spacing: int = 20,
        strategy: str = "free",
        min_columns: int = 3,
        max_columns: int = 6,
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
            min_columns=min_columns,
            max_columns=max_columns,
        )

        self.renderer = DashboardRenderer(
            owner=self,
            layout_engine=self.layout_engine,
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

        self.auto_scroll = DashboardAutoScroll(self)
        if strategy == "sequential":
            self.layout_strategy = SequentialStrategy(self)
        else:
            self.layout_strategy = FreePositionStrategy(self)

        self.drag_engine = DashboardDragEngine(self)

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

        if hasattr(self.layout_strategy, "recompute_all_positions"):
            self.layout_strategy.recompute_all_positions()

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

        return self.layout_strategy.find_available_position(
            width_units,
            height_units,
        )

    def _can_place_card(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> bool:

        return self.layout_strategy.can_place_card(
            row,
            column,
            width_units,
            height_units,
        )

    def _mark_cells_as_occupied(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        self.layout_strategy.mark_cells_as_occupied(
            row,
            column,
            width_units,
            height_units,
        )

    def get_cards_in_area(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> list:

        return self.drag_engine.get_cards_in_area(
            row,
            column,
            width_units,
            height_units,
        )

    def can_drop_card_at(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> bool:

        return self.drag_engine.can_drop_card_at(
            row,
            column,
            width_units,
            height_units,
        )

    def _clear_layout(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)

            if item.widget():
                self.layout.removeWidget(item.widget())

    def get_cell_from_global_position(
            self,
            global_pos,
    ) -> tuple[int, int] | None:

        return self.drag_engine.get_cell_from_global_position(
            global_pos
        )

    def show_drop_preview(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
            valid: bool,
    ) -> None:

        self.drag_engine.show_drop_preview(
            row,
            column,
            width_units,
            height_units,
            valid,
        )

    def hide_drop_preview(self) -> None:
        self.drag_engine.hide_drop_preview()

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

        self.drag_engine.move_card_to(
            widget,
            row,
            column,
        )

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

        self.layout_strategy.move_card_with_push(
            moved_widget,
            target_row,
            target_column,
            width_units,
            height_units,
        )

    def _find_available_position_from(
            self,
            start_row: int,
            start_column: int,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int]:

        return self.layout_strategy.find_available_position_from(
            start_row,
            start_column,
            width_units,
            height_units,
        )

    def _apply_widget_span_size(
            self,
            widget,
            width_units: int,
            height_units: int,
    ) -> None:

        self.renderer.apply_widget_span_size(
            widget,
            width_units,
            height_units,
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
        self.auto_scroll.start()

    def stop_drag_auto_scroll(self) -> None:
        self.auto_scroll.stop()

    def update_drag_auto_scroll(self, global_pos) -> None:
        self.auto_scroll.update(global_pos)

    def _perform_auto_scroll(self) -> None:
        self.auto_scroll.perform()

    def _stop_auto_scroll(self) -> None:
        self.auto_scroll.stop()

    def _get_scroll_area_parent(self) -> QScrollArea | None:
        return self.auto_scroll._get_scroll_area_parent()

    def _update_minimum_grid_height(self) -> None:
        self.renderer.update_minimum_grid_height()

    def _apply_fixed_grid_tracks(
            self,
            cell_width: int,
            cell_height: int,
    ) -> None:

        self.renderer.apply_fixed_grid_tracks(
            cell_width,
            cell_height,
        )

    def _clear_unused_grid_tracks(self) -> None:
        self.renderer.clear_unused_grid_tracks()

    def _update_debug_cells(self) -> None:
        self.renderer.update_debug_cells()

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

        self.renderer.place_widget_on_grid(
            widget,
            row,
            column,
            width_units,
            height_units,
        )

    def confirm_layout_changes(
            self,
    ) -> None:

        self.snapshot.clear()