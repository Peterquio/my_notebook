class FreePositionStrategy:
    def __init__(
            self,
            owner,
    ) -> None:

        self.owner = owner

    def find_available_position(
            self,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int]:

        row = 0

        while True:
            for column in range(self.owner.current_columns):
                if self.can_place_card(
                    row,
                    column,
                    width_units,
                    height_units,
                ):
                    return row, column

            row += 1

    def can_place_card(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> bool:

        if column + width_units > self.owner.current_columns:
            return False

        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                if (r, c) in self.owner.occupied_cells:
                    return False

        return True

    def mark_cells_as_occupied(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                self.owner.occupied_cells.append((r, c))

    def find_available_position_from(
            self,
            start_row: int,
            start_column: int,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int]:

        row = start_row
        column = start_column

        while True:
            while column < self.owner.current_columns:
                if self.can_place_card(
                    row,
                    column,
                    width_units,
                    height_units,
                ):
                    return row, column

                column += 1

            row += 1
            column = 0

    def move_card_with_push(
            self,
            moved_widget,
            target_row: int,
            target_column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        old_positions = {
            widget: position.copy()
            for widget, position in self.owner.card_positions.items()
        }

        ordered_widgets = sorted(
            old_positions.keys(),
            key=lambda widget: (
                old_positions[widget]["row"],
                old_positions[widget]["column"],
            ),
        )

        self.owner.card_positions = {}
        self.owner.occupied_cells = []

        self.owner.card_positions[moved_widget] = {
            "row": target_row,
            "column": target_column,
            "width_units": width_units,
            "height_units": height_units,
        }

        self.mark_cells_as_occupied(
            target_row,
            target_column,
            width_units,
            height_units,
        )

        for widget in ordered_widgets:
            if widget == moved_widget:
                continue

            if widget == self.owner.add_card_button:
                continue

            old_position = old_positions[widget]

            old_row = old_position["row"]
            old_column = old_position["column"]
            old_width_units = old_position["width_units"]
            old_height_units = old_position["height_units"]

            if self.can_place_card(
                    old_row,
                    old_column,
                    old_width_units,
                    old_height_units,
            ):
                new_row = old_row
                new_column = old_column
            else:
                new_row, new_column = self.find_available_position_from(
                    old_row,
                    old_column,
                    old_width_units,
                    old_height_units,
                )

            self.owner.card_positions[widget] = {
                "row": new_row,
                "column": new_column,
                "width_units": old_width_units,
                "height_units": old_height_units,
            }

            self.mark_cells_as_occupied(
                new_row,
                new_column,
                old_width_units,
                old_height_units,
            )