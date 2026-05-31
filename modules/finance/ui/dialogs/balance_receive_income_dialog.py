from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class BalanceReceiveIncomeDialog(QDialog):
    def __init__(
            self,
            income_data: dict,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.income_data = income_data

        self.setWindowTitle("Receber receita")
        self.setMinimumWidth(380)

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        titulo = QLabel("Receber receita")
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        descricao = QLabel(
            self.income_data["description"]
        )
        descricao.setStyleSheet(
            "font-size: 13px; color: #475569;"
        )

        self.amount_input = QLineEdit()
        self.amount_input.setText(
            self._formatar_centavos_para_texto(
                self.income_data["expected_amount_cents"]
            )
        )
        self.amount_input.textChanged.connect(
            self._formatar_valor_digitado
        )

        self.received_date_input = QDateEdit()
        self.received_date_input.setCalendarPopup(True)
        self.received_date_input.setDisplayFormat("dd/MM/yyyy")
        self.received_date_input.setDate(QDate.currentDate())

        layout.addWidget(titulo)
        layout.addWidget(descricao)

        layout.addWidget(QLabel("Valor recebido"))
        layout.addWidget(self.amount_input)

        layout.addWidget(QLabel("Data de recebimento"))
        layout.addWidget(self.received_date_input)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        confirmar = QPushButton("Confirmar")
        confirmar.clicked.connect(self._confirmar)

        botoes.addWidget(cancelar)
        botoes.addWidget(confirmar)

        layout.addLayout(botoes)

    def _formatar_valor_digitado(self) -> None:
        texto = self.amount_input.text()

        apenas_digitos = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        if not apenas_digitos:
            return

        texto_formatado = self._formatar_centavos_para_texto(
            int(apenas_digitos)
        )

        if texto == texto_formatado:
            return

        self.amount_input.blockSignals(True)
        self.amount_input.setText(texto_formatado)
        self.amount_input.setCursorPosition(len(texto_formatado))
        self.amount_input.blockSignals(False)

    def _formatar_centavos_para_texto(
            self,
            valor_cents: int,
    ) -> str:
        valor = valor_cents / 100
        texto = f"{valor:,.2f}"

        return (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _converter_texto_para_centavos(
            self,
            texto: str,
    ) -> int:
        apenas_digitos = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        if not apenas_digitos:
            return 0

        return int(apenas_digitos)

    def _confirmar(self) -> None:
        if self._converter_texto_para_centavos(self.amount_input.text()) <= 0:
            QMessageBox.warning(
                self,
                "Valor inválido",
                "Informe um valor maior que zero.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        return {
            "valor_real_cents": self._converter_texto_para_centavos(
                self.amount_input.text()
            ),
            "received_date": self.received_date_input.date().toString("yyyy-MM-dd"),
        }