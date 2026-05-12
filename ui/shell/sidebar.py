#Cria sidebar + área de conteúdo

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master,
            width=260,
            corner_radius=0,
        )

        self.grid(row=0, column=0, sticky="ns")

        self.grid_propagate(False)

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        titulo = ctk.CTkLabel(
            self,
            text="My Notebook",
            font=("Segoe UI", 22, "bold"),
        )

        titulo.pack(
            padx=20,
            pady=(30, 20),
            anchor="w",
        )

        dashboard_btn = ctk.CTkButton(
            self,
            text="Dashboard",
        )

        dashboard_btn.pack(
            fill="x",
            padx=15,
            pady=5,
        )

        finance_btn = ctk.CTkButton(
            self,
            text="Financeiro",
        )

        finance_btn.pack(
            fill="x",
            padx=15,
            pady=5,
        )

        tasker_btn = ctk.CTkButton(
            self,
            text="Tasker",
        )

        tasker_btn.pack(
            fill="x",
            padx=15,
            pady=5,
        )