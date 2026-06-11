from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.finance.ui.balance_accounts_page import (
    BalanceAccountsPage,
)

from modules.finance.ui.balance_income_page import (
    BalanceIncomePage,
)

from modules.finance.ui.balance_commitment_page import (
    BalanceCommitmentPage,
)

from modules.finance.ui.balance_dashboard_page import (
    BalanceDashboardPage,
)

from modules.finance.ui.monthly_templates_page import (
    MonthlyTemplatesPage,
)

from modules.finance.ui.balance_timeline_page import (
    BalanceTimelinePage,
)

class BalanceDetailWindow(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username

        self._aplicar_estilo_base()
        self._montar_interface()

    def _aplicar_estilo_base(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f8fafc;
                font-family: Segoe UI;
                color: #0f172a;
            }

            QLabel {
                color: #0f172a;
            }

            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 12px;
                color: #334155;
                font-size: 12px;
            }

            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 14px;
                color: #334155;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                gridline-color: #eef2f7;
                selection-background-color: #ede9fe;
                selection-color: #1e1b4b;
                font-size: 12px;
            }

            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-size: 11px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 10px;
            }
            """
        )

    def _montar_interface(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(
            self._criar_sidebar()
        )

        main_layout.addWidget(
            self._criar_area_principal(),
            1,
        )

    def _criar_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-right: 1px solid #e2e8f0;
            }
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(10)

        logo = QLabel("Saldo")
        logo.setStyleSheet(
            """
            color: #16a34a;
            font-size: 26px;
            font-weight: bold;
            """
        )

        layout.addWidget(logo)
        layout.addSpacing(28)

        botoes = [
            ("Dashboard", True),
            ("Timeline", False),
            ("Contas", False),
            ("Receitas", False),
            ("Compromissos", False),
            ("Modelos Mensais", False),
        ]

        self.sidebar_buttons = {}

        for texto, ativo in botoes:
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(
                self._estilo_botao_sidebar(ativo)
            )

            self.sidebar_buttons[texto] = botao

            if texto == "Dashboard":
                botao.clicked.connect(
                    self._mostrar_dashboard
                )

            if texto == "Contas":
                botao.clicked.connect(
                    self._mostrar_contas
                )

            if texto == "Receitas":
                botao.clicked.connect(
                    self._mostrar_receitas
                )

            if texto == "Compromissos":
                botao.clicked.connect(
                    self._mostrar_compromissos
                )

            if texto == "Modelos Mensais":
                botao.clicked.connect(
                    self._mostrar_modelos_mensais
                )

            if texto == "Timeline":
                botao.clicked.connect(
                    self._mostrar_timeline
                )

            layout.addWidget(botao)

        layout.addStretch()

        sair = QPushButton("Sair")
        sair.clicked.connect(
            self.back_requested.emit
        )
        sair.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: #475569;
                border: none;
                text-align: left;
                padding: 10px 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
            }
            """
        )

        layout.addWidget(sair)

        return sidebar

    def _estilo_botao_sidebar(
            self,
            ativo: bool,
    ) -> str:
        if ativo:
            return """
                QPushButton {
                    background-color: #dcfce7;
                    color: #15803d;
                    border: 1px solid #bbf7d0;
                    border-radius: 12px;
                    font-weight: bold;
                    text-align: left;
                    padding: 11px 12px;
                }

                QPushButton:hover {
                    background-color: #bbf7d0;
                }
            """

        return """
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                text-align: left;
                padding: 11px 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #cbd5e1;
            }
        """

    def _atualizar_botao_ativo(
            self,
            nome_botao: str,
    ) -> None:
        for nome, botao in self.sidebar_buttons.items():
            botao.setStyleSheet(
                self._estilo_botao_sidebar(
                    ativo=nome == nome_botao
                )
            )

    def _criar_area_principal(self) -> QWidget:
        container = QWidget()

        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self._mostrar_dashboard()

        return container

    def _limpar_area_principal(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _mostrar_dashboard(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Dashboard")

        self.dashboard_page = BalanceDashboardPage(
            username=self.username,
            parent=self,
        )

        self.content_layout.addWidget(
            self.dashboard_page
        )

    def _mostrar_contas(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Contas")

        self.accounts_page = BalanceAccountsPage(
            username=self.username,
            parent=self,
        )

        self.accounts_page.data_changed.connect(
            self.data_changed.emit
        )

        self.content_layout.addWidget(
            self.accounts_page
        )

    def _mostrar_receitas(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Receitas")

        self.income_page = BalanceIncomePage(
            username=self.username,
            parent=self,
        )

        self.content_layout.addWidget(
            self.income_page
        )

    def _mostrar_compromissos(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Compromissos")

        self.commitment_page = BalanceCommitmentPage(
            username=self.username,
            parent=self,
        )

        self.content_layout.addWidget(
            self.commitment_page
        )

    def _mostrar_modelos_mensais(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Modelos Mensais")

        self.monthly_templates_page = MonthlyTemplatesPage(
            username=self.username,
            parent=self,
        )

        self.monthly_templates_page.data_changed.connect(
            self.data_changed.emit
        )

        self.content_layout.addWidget(
            self.monthly_templates_page
        )

    def _mostrar_timeline(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Timeline")

        self.timeline_page = BalanceTimelinePage(
            username=self.username,
            parent=self,
        )

        self.content_layout.addWidget(
            self.timeline_page
        )