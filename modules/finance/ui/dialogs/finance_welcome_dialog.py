from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class FinanceWelcomeDialog(QDialog):
    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Bem-vindo ao Financeiro")
        self.setMinimumWidth(460)

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(14)

        titulo = QLabel("Bem-vindo ao módulo Financeiro")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        texto = QLabel(
            "Aqui você poderá organizar suas contas, receitas, compromissos "
            "e futuramente integrar seus cartões de crédito ao saldo.\n\n"
            "Para começar, vamos criar seu primeiro ciclo financeiro."
        )
        texto.setWordWrap(True)
        texto.setStyleSheet(
            "font-size: 13px; color: #475569; line-height: 1.4;"
        )

        botoes = QHBoxLayout()
        botoes.addStretch()

        comecar = QPushButton("Começar")
        comecar.clicked.connect(self.accept)

        botoes.addWidget(comecar)

        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addLayout(botoes)