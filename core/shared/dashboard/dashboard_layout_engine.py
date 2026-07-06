class DashboardLayoutEngine:
    def __init__(
            self,
            min_cell_width: int = 240,
            max_cell_width: int = 300,
            cell_ratio: float = 0.70,
            spacing: int = 20,
            max_columns: int = 6,
            min_columns: int = 3,
    ) -> None:
        self.min_cell_width = min_cell_width
        self.max_cell_width = max_cell_width
        self.cell_ratio = cell_ratio
        self.spacing = spacing
        self.max_columns = max_columns
        self.min_columns = min_columns

    def calculate_columns(
            self,
            available_width: int,
    ) -> int:
        minimum_column_width = (
            self.min_cell_width
            + self.spacing
        )

        columns = available_width // minimum_column_width

        return min(
            self.max_columns,
            max(
                self.min_columns,
                columns,
            ),
        )

    def calculate_cell_width(
            self,
            available_width: int,
            columns: int,
    ) -> int:
        return self.min_cell_width

    def calculate_cell_height(
            self,
            cell_width: int,
    ) -> int:
        return int(
            cell_width
            * self.cell_ratio
        )

    def parse_size(
            self,
            size: str,
    ) -> tuple[int, int]:
        width, height = size.lower().split("x")

        return int(width), int(height)

    def get_grid_geometry(
            self,
            row: int,
            column: int,
            width_units: int,
            height_units: int,
            cell_width: int,
            cell_height: int,
    ) -> tuple[int, int, int, int]:

        x = column * (
            cell_width
            + self.spacing
        )

        y = row * (
            cell_height
            + self.spacing
        )

        width = (
            cell_width * width_units
            + self.spacing * (width_units - 1)
        )

        height = (
            cell_height * height_units
            + self.spacing * (height_units - 1)
        )

        return x, y, width, height

    def calculate_minimum_height(
            self,
            total_rows: int,
            cell_height: int,
    ) -> int:
        return (
            total_rows * cell_height
            + max(0, total_rows - 1) * self.spacing
        )