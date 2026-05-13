from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton


class Sidebar(QFrame):
    navigate_requested = Signal(str)

    def __init__(self):
        super().__init__()

        self.buttons = {}
        self.selected_module = "dashboard"

        self.setFixedWidth(260)
        self.setObjectName("Sidebar")

        self._criar_layout()
        self._criar_widgets()

    def _criar_layout(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 30, 20, 20)
        self.layout.setSpacing(10)

    def _criar_widgets(self) -> None:
        title = QLabel("My Notebook")
        title.setObjectName("SidebarTitle")
        self.layout.addWidget(title)

        self.layout.addSpacing(15)

        itens_menu = [
            ("dashboard", "Dashboard"),
            ("finance", "Financeiro"),
            ("tasker", "Tasker"),
            ("planner", "Planner"),
            ("diary", "Diário"),
            ("calendar", "Calendário"),
        ]

        for module_name, label in itens_menu:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setObjectName("SidebarButton")
            button.clicked.connect(
                lambda checked=False, name=module_name: self._navegar(name)
            )

            self.layout.addWidget(button)
            self.buttons[module_name] = button

        self.layout.addStretch()
        self._atualizar_botao_selecionado()

    def _navegar(self, module_name: str) -> None:
        self.selected_module = module_name
        self._atualizar_botao_selecionado()
        self.navigate_requested.emit(module_name)

    def _atualizar_botao_selecionado(self) -> None:
        for name, button in self.buttons.items():
            button.setChecked(name == self.selected_module)