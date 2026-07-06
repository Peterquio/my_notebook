class DashboardDragEngine:
    def __init__(
            self,
            owner,
    ) -> None:
        self.owner = owner

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

        for widget, position in list(self.owner.card_positions.items()):
            if (
                    widget == self.owner.add_card_button
                    and not self.owner.edit_mode
            ):
                widget.hide()
                continue

            widget_cells = set()

            for r in range(
                    position["row"],
                    position["row"] + position["height_units"],
            ):
                for c in range(
                        position["column"],
                        position["column"] + position["width_units"],
                ):
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
        return column + width_units <= self.owner.current_columns

    def get_cell_from_global_position(
            self,
            global_pos,
    ) -> tuple[int, int] | None:
        local_pos = self.owner.mapFromGlobal(global_pos)

        if not self.owner.rect().contains(local_pos):
            return None

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
                cell_rect = self.owner.layout.cellRect(row, column)

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
        x, y, width, height = self.owner._get_grid_geometry(
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

        self.owner.drop_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px dashed {border};
                border-radius: 18px;
            }}
        """)

        self.owner.drop_preview.setGeometry(
            x,
            y,
            width,
            height,
        )

        self.owner.drop_preview.show()
        self.owner.drop_preview.raise_()

    def hide_drop_preview(self) -> None:
        self.owner.drop_preview.hide()
        self.owner._stop_auto_scroll()

    def move_card_to(
            self,
            widget,
            row: int,
            column: int,
    ) -> None:
        if widget not in self.owner.card_positions:
            return

        position = self.owner.card_positions[widget]

        width_units = position["width_units"]
        height_units = position["height_units"]

        if column + width_units > self.owner.current_columns:
            return

        self.owner._move_card_with_push(
            widget,
            row,
            column,
            width_units,
            height_units,
        )

        if self.owner.edit_mode:
            self.owner._update_add_card_button_position()

        self.owner._rebuild_grid_from_positions()