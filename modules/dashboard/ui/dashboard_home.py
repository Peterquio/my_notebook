#Cria a UI principal do Dashboard

import customtkinter as ctk


class DashboardHome(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)

        self.grid_columnconfigure(0, weight=1)

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        titulo = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Segoe UI", 28, "bold"),
        )

        titulo.grid(
            row=0,
            column=0,
            padx=30,
            pady=(30, 10),
            sticky="w",
        )

        subtitulo = ctk.CTkLabel(
            self,
            text="Visão geral do seu sistema pessoal.",
            font=("Segoe UI", 15),
        )

        subtitulo.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 20),
            sticky="w",
        )