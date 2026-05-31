from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class BalanceAccountDialog(QDialog):
    def __init__(
            self,
            account_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.account_data = account_data

        self.setWindowTitle(
            "Editar conta" if account_data else "Nova conta"
        )

        self.setMinimumWidth(420)

        self._montar_interface()

        if self.account_data:
            self._carregar_dados()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        titulo = QLabel(
            "Editar conta financeira" if self.account_data else "Nova conta financeira"
        )
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        layout.addWidget(titulo)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex.: Nubank, Inter, Carteira")

        self.type_combo = QComboBox()
        self.type_combo.addItem("Banco", "bank")
        self.type_combo.addItem("Carteira", "wallet")
        self.type_combo.addItem("Dinheiro", "cash")

        self.global_checkbox = QCheckBox("Participa do saldo global")
        self.global_checkbox.setChecked(True)

        self.investment_checkbox = QCheckBox("Conta de investimento")

        layout.addWidget(QLabel("Nome"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(self.type_combo)

        layout.addWidget(self.global_checkbox)
        layout.addWidget(self.investment_checkbox)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self._salvar)

        botoes.addWidget(cancelar)
        botoes.addWidget(salvar)

        layout.addLayout(botoes)

    def _carregar_dados(self) -> None:
        self.name_input.setText(
            self.account_data["name"]
        )

        index = self.type_combo.findData(
            self.account_data["account_type"]
        )

        if index >= 0:
            self.type_combo.setCurrentIndex(index)

        self.global_checkbox.setChecked(
            bool(self.account_data["include_in_global_balance"])
        )

        self.investment_checkbox.setChecked(
            bool(self.account_data["is_investment"])
        )

    def _salvar(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Nome obrigatório",
                "Informe o nome da conta.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "account_type": self.type_combo.currentData(),
            "include_in_global_balance": self.global_checkbox.isChecked(),
            "is_investment": self.investment_checkbox.isChecked(),
        }