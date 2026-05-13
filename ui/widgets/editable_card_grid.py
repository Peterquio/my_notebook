import customtkinter as ctk


class EditableCardGrid(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns: int = 4,
        unit_width: int = 140,
        unit_height: int = 120,
        spacing: int = 15,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.columns = columns
        self.unit_width = unit_width
        self.unit_height = unit_height
        self.spacing = spacing
        self.edit_mode = False

        self.occupied_cells = []

    def add_card(
        self,
        card,
        size: str = "1x1",
    ) -> None:
        width_units, height_units = self._parse_size(size)

        row, column = self._find_available_position(
            width_units,
            height_units,
        )

        self._mark_cells_as_occupied(
            row,
            column,
            width_units,
            height_units,
        )

        card.configure(
            width=self._calculate_width(width_units),
            height=self._calculate_height(height_units),
        )

        card.grid(
            row=row,
            column=column,
            columnspan=width_units,
            rowspan=height_units,
            padx=self.spacing,
            pady=self.spacing,
            sticky="nsew",
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
            for column in range(self.columns):
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
        if column + width_units > self.columns:
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

    def _calculate_width(self, units: int) -> int:
        return (self.unit_width * units) + (
            self.spacing * 2 * (units - 1)
        )

    def _calculate_height(self, units: int) -> int:
        return (self.unit_height * units) + (
            self.spacing * 2 * (units - 1)
        )

    def set_edit_mode(self, enabled: bool) -> None:
        self.edit_mode = enabled

        if enabled:
            self.configure(
                fg_color="#f3f4f6",
            )
        else:
            self.configure(
                fg_color="transparent",
            )