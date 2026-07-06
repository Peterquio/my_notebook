from PySide6.QtWidgets import QFrame


class DashboardRenderer:
    def __init__(
            self,
            owner,
            layout_engine,
    ) -> None:
        self.owner = owner
        self.layout_engine = layout_engine

    def apply_widget_span_size(
            self,
            widget,
            width_units: int,
            height_units: int,
    ) -> None:

        real_width = (
            self.owner._last_cell_width * width_units
            + self.owner.spacing * (width_units - 1)
        )

        real_height = (
            self.owner._last_cell_height * height_units
            + self.owner.spacing * (height_units - 1)
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

    def place_widget_on_grid(
            self,
            widget,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        self.apply_widget_span_size(
            widget,
            width_units,
            height_units,
        )

        x, y, width, height = self.owner._get_grid_geometry(
            row,
            column,
            width_units,
            height_units,
        )

        widget.setParent(self.owner)
        widget.setGeometry(x, y, width, height)
        widget.show()
        widget.raise_()

    def apply_fixed_grid_tracks(
            self,
            cell_width: int,
            cell_height: int,
    ) -> None:

        self.clear_unused_grid_tracks()

        for column in range(self.owner.current_columns):
            self.owner.layout.setColumnMinimumWidth(
                column,
                cell_width,
            )

            self.owner.layout.setColumnStretch(
                column,
                0,
            )

        spacer_column = self.owner.current_columns

        self.owner.layout.setColumnMinimumWidth(
            spacer_column,
            0,
        )

        self.owner.layout.setColumnStretch(
            spacer_column,
            1,
        )

        max_row = 0

        for position in self.owner.card_positions.values():
            max_row = max(
                max_row,
                position["row"] + position["height_units"],
            )

        total_rows = max_row + getattr(
            self.owner,
            "extra_drop_rows",
            0,
        )

        for row in range(total_rows):
            self.owner.layout.setRowMinimumHeight(
                row,
                cell_height,
            )

            self.owner.layout.setRowStretch(
                row,
                0,
            )

    def clear_unused_grid_tracks(self) -> None:
        for row in range(100):
            self.owner.layout.setRowMinimumHeight(row, 0)
            self.owner.layout.setRowStretch(row, 0)

        for column in range(20):
            self.owner.layout.setColumnMinimumWidth(column, 0)
            self.owner.layout.setColumnStretch(column, 0)

    def update_minimum_grid_height(self) -> None:
        if not self.owner.card_positions:
            return

        used_rows = max(
            position["row"] + position["height_units"]
            for position in self.owner.card_positions.values()
        )

        total_rows = used_rows + self.owner.extra_drop_rows

        minimum_height = (
            self.layout_engine.calculate_minimum_height(
                total_rows=total_rows,
                cell_height=self.owner._last_cell_height,
            )
        )

        self.owner.setMinimumHeight(minimum_height)

    def update_debug_cells(self) -> None:
        for frame in self.owner.debug_cell_frames:
            frame.deleteLater()

        self.owner.debug_cell_frames = []

        if not self.owner.debug_show_cells:
            return

        used_rows = max(
            (
                position["row"] + position["height_units"]
                for position in self.owner.card_positions.values()
            ),
            default=0,
        )

        total_rows = used_rows + self.owner.extra_drop_rows

        for row in range(total_rows):
            for column in range(self.owner.current_columns):
                x, y, width, height = self.owner._get_grid_geometry(
                    row,
                    column,
                    1,
                    1,
                )

                frame = QFrame(self.owner)
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

                self.owner.debug_cell_frames.append(frame)