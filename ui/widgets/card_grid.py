import customtkinter as ctk


class CardGrid(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns: int = 3,
        spacing: int = 15,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.columns = columns
        self.spacing = spacing
        self.current_index = 0

        for column in range(columns):
            self.grid_columnconfigure(
                column,
                weight=1,
            )

    def add_card(self, card) -> None:
        row = self.current_index // self.columns
        column = self.current_index % self.columns

        card.grid(
            row=row,
            column=column,
            padx=self.spacing,
            pady=self.spacing,
            sticky="nw",
        )

        self.current_index += 1