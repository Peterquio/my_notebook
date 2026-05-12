#Ele cria a janela base do app usando as configurações centralizadas em:
#core/config/app_config.py
#Ou seja, nada de tamanho hardcoded espalhado. :)

import customtkinter as ctk

from core.config.app_config import (
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
)
from ui.shell.sidebar import Sidebar
from ui.shell.navigation_manager import NavigationManager
from modules.dashboard.ui.dashboard_home import DashboardHome

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self._configurar_grid()
        self.sidebar = Sidebar(self)

        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.navigation_manager = NavigationManager(self.content_frame)
        self.navigation_manager.registrar_tela(
            "dashboard",
            lambda master: DashboardHome(master),
        )
        self.navigation_manager.navegar_para("dashboard")

        

    def _configurar_grid(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)