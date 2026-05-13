from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self._criar_layout()
        self._registrar_telas()
        self._aplicar_estilo()

        self.navigation_manager.navegar_para("dashboard")

    def _criar_layout(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigate_requested.connect(self._navegar_para)

        self.content_stack = QStackedWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_stack, stretch=1)

        self.navigation_manager = NavigationManager(self.content_stack)

    def _registrar_telas(self) -> None:
        self.navigation_manager.registrar_tela(
            "dashboard",
            lambda: DashboardHome(),
        )

        self.navigation_manager.registrar_tela(
            "finance",
            lambda: FinanceHome(),
        )

        self.navigation_manager.registrar_tela(
            "tasker",
            lambda: TaskerHome(),
        )

        self.navigation_manager.registrar_tela(
            "planner",
            lambda: PlannerHome(),
        )

        self.navigation_manager.registrar_tela(
            "diary",
            lambda: DiaryHome(),
        )

        self.navigation_manager.registrar_tela(
            "calendar",
            lambda: CalendarHome(),
        )

    def _navegar_para(self, nome_tela: str) -> None:
        self.navigation_manager.navegar_para(nome_tela)

    def _aplicar_estilo(self) -> None:
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }

            #Sidebar {
                background-color: #111827;
            }

            #SidebarTitle {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }

            #SidebarButton {
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 10px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }

            #SidebarButton:hover {
                background-color: #1f2937;
            }

            #SidebarButton:checked {
                background-color: #2563eb;
            }

            #ScreenTitle {
                color: #111827;
                font-size: 28px;
                font-weight: bold;
            }

            #ScreenSubtitle {
                color: #64748b;
                font-size: 14px;
            }

            #ScreenContent {
                background-color: transparent;
            }
            
            #AppCard {
                background-color: white;
                border-radius: 20px;
            }

            #CardTitle {
                color: #475569;
                font-size: 14px;
                font-weight: bold;
            }
            
            #CardValue {
                color: #111827;
                font-size: 30px;
                font-weight: bold;
            }
            
            #CardSubtitle {
                color: #64748b;
                font-size: 13px;
            }
            
            #CardIcon {
                font-size: 22px;
            }
            
            #EditButton {
                background-color: white;
                border: none;
                border-radius: 14px;
                padding: 10px 14px;
                font-size: 16px;
            }
            
            #EditButton:hover {
                background-color: #e2e8f0;
            }
            
            #ScreenScroll {
                border: none;
                background-color: transparent;
            }
        """)