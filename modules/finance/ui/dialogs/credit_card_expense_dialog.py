from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from ui.widgets.date_line_edit import DateLineEdit

class CreditCardExpenseDialog(QDialog):
    def __init__(
            self,
            categories: list[dict],
            invoice_year: int,
            row_data: dict | None = None,
            mode: str = "edit",
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.categories = categories
        self.invoice_year = invoice_year
        self.row_data = row_data
        self.mode = mode

        self.setWindowTitle(
            "Novo lançamento" if mode == "create" else "Editar lançamento"
        )
        self.setMinimumWidth(480)

        self._montar_interface()
        self._preencher_dados()
        self._atualizar_estado_parcelamento()
        self._aplicar_estilo()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.descricao_input = QLineEdit()

        self.data_input = DateLineEdit()

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setMaximum(999999.99)
        self.valor_input.setDecimals(2)
        self.valor_input.setPrefix("R$ ")

        self.categoria_input = QComboBox()

        self.subcategoria_input = QLineEdit()
        self.subcategoria_input.setPlaceholderText("Ex.: Mercado, farmácia, transporte...")

        for categoria_item in self.categories:
            self.categoria_input.addItem(
                categoria_item["name"],
                categoria_item["id"],
            )

        self.parcelado_checkbox = QCheckBox("Item parcelado")

        self.parcela_atual_input = QSpinBox()
        self.parcela_atual_input.setMinimum(1)
        self.parcela_atual_input.setMaximum(999)
        self.parcela_atual_input.setValue(1)

        self.parcelas_totais_input = QSpinBox()
        self.parcelas_totais_input.setMinimum(1)
        self.parcelas_totais_input.setMaximum(999)
        self.parcelas_totais_input.setValue(1)

        self.parcelado_checkbox.stateChanged.connect(
            self._atualizar_estado_parcelamento
        )

        self.parcela_atual_input.valueChanged.connect(
            self._corrigir_limites_parcelas
        )

        self.parcelas_totais_input.valueChanged.connect(
            self._corrigir_limites_parcelas
        )

        self.observacoes_input = QTextEdit()
        self.observacoes_input.setFixedHeight(80)

        form.addRow("Descrição:", self.descricao_input)
        form.addRow("Data da parcela atual:", self.data_input)
        form.addRow("Valor da parcela:", self.valor_input)
        form.addRow("Categoria:", self.categoria_input)
        form.addRow("Subcategoria:", self.subcategoria_input)
        form.addRow("", self.parcelado_checkbox)
        form.addRow("Parcela atual:", self.parcela_atual_input)
        form.addRow("Parcelas totais:", self.parcelas_totais_input)
        form.addRow("Observações:", self.observacoes_input)

        layout.addLayout(form)

        ajuda = QLabel(
            "Para compras antigas, informe qual parcela está caindo nesta fatura. "
            "Ex.: 7/10 gera automaticamente as parcelas 1 a 10 nos meses corretos."
        )
        ajuda.setWordWrap(True)
        ajuda.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(ajuda)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        salvar = QPushButton(
            "Adicionar" if self.mode == "create" else "Salvar"
        )
        salvar.setDefault(True)
        salvar.setAutoDefault(True)

        cancelar.clicked.connect(self.reject)
        salvar.clicked.connect(self.accept)

        botoes.addWidget(cancelar)
        botoes.addWidget(salvar)

        layout.addLayout(botoes)

    def _preencher_dados(self) -> None:
        if self.mode == "create" or self.row_data is None:
            self.data_input.set_date(QDate.currentDate())
            return

        self.descricao_input.setText(
            self.row_data["description"]
        )

        dia, mes = self.row_data["date"].split("/")

        self.data_input.set_date(
            QDate(
                int(self.invoice_year),
                int(mes),
                int(dia),
            )
        )

        valor_texto = (
            self.row_data["amount"]
            .replace("R$ ", "")
            .replace(".", "")
            .replace(",", ".")
        )

        self.valor_input.setValue(float(valor_texto))

        categoria_index = self.categoria_input.findData(
            self.row_data.get("category_id")
        )

        if categoria_index >= 0:
            self.categoria_input.setCurrentIndex(categoria_index)
        self.subcategoria_input.setText(
            self.row_data.get("subcategory") or ""
        )

        installment_number = self.row_data.get("installment_number", 1)
        installment_total = self.row_data.get("installment_total", 1)

        if installment_total > 1:
            self.parcelado_checkbox.setText("Item parcelado")
            self.parcelado_checkbox.setChecked(True)
            self.parcela_atual_input.setValue(installment_number)
            self.parcelas_totais_input.setValue(installment_total)
        else:
            self.parcelado_checkbox.setText("Parcelar compra")
            self.parcelado_checkbox.setChecked(False)

    def _atualizar_estado_parcelamento(self) -> None:
        parcelado = self.parcelado_checkbox.isChecked()

        self.parcela_atual_input.setEnabled(parcelado)
        self.parcelas_totais_input.setEnabled(parcelado)

        if not parcelado:
            self.parcela_atual_input.setValue(1)
            self.parcelas_totais_input.setValue(1)

    def _corrigir_limites_parcelas(self) -> None:
        parcela_atual = self.parcela_atual_input.value()
        parcelas_totais = self.parcelas_totais_input.value()

        if parcela_atual > parcelas_totais:
            self.parcelas_totais_input.setValue(parcela_atual)

    def obter_dados(self) -> dict:
        parcelado = self.parcelado_checkbox.isChecked()

        return {
            "category_id": self.categoria_input.currentData(),
            "subcategory": self.subcategoria_input.text().strip(),
            "effective_description": self.descricao_input.text().strip(),
            "effective_purchase_date": self.data_input.to_iso_date(self.invoice_year),
            "effective_amount_cents": int(round(self.valor_input.value() * 100)),
            "notes": self.observacoes_input.toPlainText().strip(),
            "installment_number": self.parcela_atual_input.value() if parcelado else 1,
            "installment_total": self.parcelas_totais_input.value() if parcelado else 1,
        }

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
            return

        super().keyPressEvent(event)

    def _aplicar_estilo(self) -> None:
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }

            QLabel {
                color: #334155;
                font-size: 13px;
            }

            QLineEdit,
            QComboBox,
            QDoubleSpinBox,
            QSpinBox,
            QTextEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                padding: 7px 10px;
                font-size: 13px;
                color: #0f172a;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDoubleSpinBox:focus,
            QSpinBox:focus,
            QTextEdit:focus {
                border: 1px solid #2563eb;
            }

            QCheckBox {
                color: #0f172a;
                font-size: 13px;
                spacing: 8px;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 9px 18px;
                font-size: 13px;
                font-weight: 600;
                background-color: #e2e8f0;
                color: #0f172a;
            }

            QPushButton:hover {
                background-color: #cbd5e1;
            }

            QPushButton:default {
                background-color: #2563eb;
                color: white;
            }

            QPushButton:default:hover {
                background-color: #1d4ed8;
            }
        """)