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

from modules.finance.ui.finance_home import FinanceHome
from modules.tasker.ui.tasker_home import TaskerHome
from modules.planner.ui.planner_home import PlannerHome
from modules.diary.ui.diary_home import DiaryHome
from modules.calendar.ui.calendar_home import CalendarHome

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self._configurar_grid()
        self.sidebar = Sidebar(
            self,
            on_navigate=self._navegar_para,
        )

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

        self.navigation_manager.registrar_tela(
            "finance",
            lambda master: FinanceHome(master),
        )

        self.navigation_manager.registrar_tela(
            "tasker",
            lambda master: TaskerHome(master),
        )

        self.navigation_manager.registrar_tela(
            "planner",
            lambda master: PlannerHome(master),
        )

        self.navigation_manager.registrar_tela(
            "diary",
            lambda master: DiaryHome(master),
        )

        self.navigation_manager.registrar_tela(
            "calendar",
            lambda master: CalendarHome(master),
        )

    def _navegar_para(self, nome_tela: str) -> None:
        self.navigation_manager.navegar_para(nome_tela)


    def _configurar_grid(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)