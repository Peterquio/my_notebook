from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from modules.finance.ui.credit_card_invoice_page import (
    CreditCardInvoicePage,
)

from modules.finance.ui.finance_settings_page import (
    FinanceSettingsPage,
)

class CreditCardDetailWindow(QWidget):
    back_requested = Signal()
    data_changed = Signal()
    def __init__(
            self,
            credit_card: dict,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.credit_card = credit_card
        self.username = username
        self._aplicar_estilo_base()
        self._montar_interface()

    def _aplicar_estilo_base(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
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
        sidebar.setFixedWidth(150)
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

        logo = QLabel("nu")
        logo.setStyleSheet(
            """
            color: #7c3aed;
            font-size: 34px;
            font-weight: bold;
            """
        )

        layout.addWidget(logo)
        layout.addSpacing(28)

        botoes = [
            ("Dashboard", True),
            ("Categorias", False),
            ("Configurações", False),
        ]

        self.sidebar_buttons = {}
        for texto, ativo in botoes:
            botao = QPushButton(texto)
            self.sidebar_buttons[texto] = botao
            botao.setCursor(Qt.PointingHandCursor)

            if texto == "Dashboard":
                botao.clicked.connect(
                    self._mostrar_dashboard
                )

            if texto == "Configurações":
                botao.clicked.connect(
                    self._mostrar_configuracoes
                )

            botao.setStyleSheet(
                self._estilo_botao_sidebar(ativo)
            )

            layout.addWidget(botao)
        layout.addSpacing(18)

        meses_titulo = QLabel("Faturas")
        meses_titulo.setStyleSheet(
            """
            color: #64748b;
            font-size: 11px;
            font-weight: bold;
            """
        )
        layout.addWidget(meses_titulo)

        meses_visiveis = [
            "Fev/2026",
            "Mar/2026",
            "Abr/2026",
            "Mai/2026",
            "Jun/2026",
            "Jul/2026",
        ]

        for mes in meses_visiveis:
            botao_mes = QPushButton(mes)
            botao_mes.setCursor(Qt.PointingHandCursor)

            if mes == "Abr/2026":
                botao_mes.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #ede9fe;
                        color: #6d28d9;
                        border: none;
                        border-radius: 10px;
                        font-weight: bold;
                        text-align: left;
                        padding: 9px 12px;
                    }
                    """
                )
            else:
                botao_mes.setStyleSheet(
                    """
                    QPushButton {
                        background-color: white;
                        color: #64748b;
                        border: none;
                        border-radius: 10px;
                        text-align: left;
                        padding: 9px 12px;
                    }

                    QPushButton:hover {
                        background-color: #f8fafc;
                    }
                    """
                )

            layout.addWidget(botao_mes)

        layout.addStretch()

        sair = QPushButton("Sair")
        sair.clicked.connect(self.close)
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
                    background-color: #ede9fe;
                    color: #6d28d9;
                    border: 1px solid #ddd6fe;
                    border-radius: 12px;
                    font-weight: bold;
                    text-align: left;
                    padding: 11px 12px;
                }

                QPushButton:hover {
                    background-color: #ddd6fe;
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

        self.invoice_page = CreditCardInvoicePage(
            credit_card=self.credit_card,
            username=self.username,
            parent=self,
        )

        self.invoice_page.data_changed.connect(
            self.data_changed.emit
        )

        self.invoice_page.back_requested.connect(
            self.back_requested.emit
        )

        self.content_layout.addWidget(
            self.invoice_page
        )

    def _mostrar_configuracoes(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Configurações")

        self.settings_page = FinanceSettingsPage(
            username=self.username,
            parent=self,
        )

        self.content_layout.addWidget(self.settings_page)