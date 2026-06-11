from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSpinBox,
)

from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)

from modules.finance.ui.dialogs.finance_category_manager_dialog import (
    FinanceCategoryManagerDialog,
)


class FinanceSettingsPage(QWidget):
    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username
        self.settings_repository = FinanceSettingsRepository(
            username
        )
        self._montar_interface()



    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        titulo = QLabel("Configurações")
        titulo.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo = QLabel(
            "Gerencie preferências globais do módulo financeiro."
        )
        subtitulo.setStyleSheet(
            "font-size: 13px; color: #64748b;"
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        layout.addWidget(
            self._criar_card_categorias()
        )

        layout.addWidget(
            self._criar_card_periodo_financeiro()
        )

        layout.addStretch()

    def _criar_card_categorias(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        textos = QVBoxLayout()
        textos.setSpacing(4)

        titulo = QLabel("Categorias de Gastos")
        titulo.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        descricao = QLabel(
            "Cadastre, edite e organize as categorias globais usadas nos cartões."
        )
        descricao.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        textos.addWidget(titulo)
        textos.addWidget(descricao)

        botao = QPushButton("Gerenciar")
        botao.setCursor(Qt.PointingHandCursor)
        botao.clicked.connect(self._abrir_categorias)
        botao.setFixedWidth(120)
        botao.setStyleSheet(
            """
            QPushButton {
                background-color: #6d28d9;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 14px;
            }

            QPushButton:hover {
                background-color: #5b21b6;
            }
            """
        )

        layout.addLayout(textos, 1)
        layout.addWidget(botao)

        return card

    def _abrir_categorias(self) -> None:
        dialog = FinanceCategoryManagerDialog(
            username=self.username,
            parent=self,
        )

        dialog.exec()

    def _criar_card_periodo_financeiro(self) -> QFrame:
        card = QFrame()

        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)

        textos = QVBoxLayout()

        titulo = QLabel("Período Financeiro")

        titulo.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        descricao = QLabel(
            "Defina o dia de referência utilizado para organizar "
            "timeline, relatórios e períodos financeiros."
        )

        descricao.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        textos.addWidget(titulo)
        textos.addWidget(descricao)

        self.reference_day_input = QSpinBox()
        self.reference_day_input.setRange(1, 31)

        self.reference_day_input.setValue(
            self.settings_repository.obter_reference_day()
        )

        salvar = QPushButton("Salvar")
        salvar.setFixedWidth(120)
        salvar.clicked.connect(
            self._salvar_reference_day
        )

        layout.addLayout(textos, 1)
        layout.addWidget(self.reference_day_input)
        layout.addWidget(salvar)

        return card

    def _salvar_reference_day(self) -> None:
        self.settings_repository.salvar_reference_day(
            self.reference_day_input.value()
        )