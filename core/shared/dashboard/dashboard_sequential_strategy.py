class SequentialStrategy:
    def __init__(
            self,
            owner,
    ) -> None:
        self.owner = owner

    def _ordered_widgets(self) -> list:
        return [
            item["widget"]
            for item in self.owner.items
            if item["widget"] != self.owner.add_card_button
        ]

    def recompute_all_positions(self) -> None:
        widgets = self._ordered_widgets()

        self.owner.card_positions = {}
        self.owner.occupied_cells = []

        for index, widget in enumerate(widgets):
            row, column = self._index_to_position(index)

            self.owner.card_positions[widget] = {
                "row": row,
                "column": column,
                "width_units": 1,
                "height_units": 1,
            }

            self.mark_cells_as_occupied(
                row=row,
                column=column,
                width_units=1,
                height_units=1,
            )

    def find_available_position(
            self,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int]:

        widgets = self._ordered_widgets()
        index = max(0, len(widgets) - 1)

        return self._index_to_position(index)

    def can_place_card(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> bool:

        return column < self.owner.current_columns

    def mark_cells_as_occupied(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        self.owner.occupied_cells.append(
            (row, column)
        )

    def find_available_position_from(
            self,
            start_row: int,
            start_column: int,
            width_units: int,
            height_units: int,
    ) -> tuple[int, int]:

        return start_row, start_column

    def move_card_with_push(
            self,
            moved_widget,
            target_row: int,
            target_column: int,
            width_units: int,
            height_units: int,
    ) -> None:

        widgets = self._ordered_widgets()

        if moved_widget not in widgets:
            return

        widgets.remove(moved_widget)

        target_index = self._position_to_index(
            target_row,
            target_column,
        )

        target_index = max(
            0,
            min(
                target_index,
                len(widgets),
            ),
        )

        widgets.insert(
            target_index,
            moved_widget,
        )

        self.owner.items = [
            {
                "widget": widget,
                "size": "1x1",
            }
            for widget in widgets
        ]

        if (
                self.owner.edit_mode
                and self.owner.add_card_button not in widgets
        ):
            self.owner.items.append(
                {
                    "widget": self.owner.add_card_button,
                    "size": "1x1",
                }
            )

        self.recompute_all_positions()

    def _index_to_position(
            self,
            index: int,
    ) -> tuple[int, int]:

        columns = max(
            1,
            self.owner.current_columns,
        )

        row = index // columns
        column = index % columns

        return row, column

    def _position_to_index(
            self,
            row: int,
            column: int,
    ) -> int:

        columns = max(
            1,
            self.owner.current_columns,
        )

        return row * columns + column