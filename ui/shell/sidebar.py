#Cria sidebar + área de conteúdo

import customtkinter as ctk
from ui.widgets.sidebar_button import SidebarButton
from core.themes import theme_tokens
from ui.widgets.sidebar_title import SidebarTitle
from ui.widgets.sidebar_separator import SidebarSeparator

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(
            master,
            width=260,
            corner_radius=0,
            fg_color=theme_tokens.SIDEBAR_BG,
        )
        self.on_navigate = on_navigate

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_propagate(False)

        self.buttons = {}
        self.selected_module = "dashboard"

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        titulo = SidebarTitle(
            self,
            text="My Notebook",
        )

        titulo.pack(
            padx=20,
            pady=(30, 20),
            anchor="w",
        )

        separador = SidebarSeparator(self)

        separador.pack(
            padx=20,
            pady=(0, 15),
            anchor="w",
        )

        itens_menu = [
            ("dashboard", "Dashboard"),
            ("finance", "Financeiro"),
            ("tasker", "Tasker"),
            ("planner", "Planner"),
            ("diary", "Diário"),
            ("calendar", "Calendário"),
        ]

        for module_name, label in itens_menu:
            button = SidebarButton(
                self,
                text=label,
                selected=module_name == self.selected_module,
                command=lambda name=module_name: self._navegar(name),
            )

            button.pack(
                fill="x",
                padx=15,
                pady=5,
            )

            self.buttons[module_name] = button

    def _navegar(self, module_name: str) -> None:
        self.selected_module = module_name

        for name, button in self.buttons.items():
            button.set_selected(name == module_name)

        self.on_navigate(module_name)
