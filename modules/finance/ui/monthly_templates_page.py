from datetime import date
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

from modules.finance.services.balance_account_service import (
    BalanceAccountService,
)
from modules.finance.services.monthly_template_service import (
    MonthlyTemplateService,
)

from modules.finance.services.monthly_template_materialization_service import (
    MonthlyTemplateMaterializationService,
)

class MonthlyTemplatesPage(QWidget):
    data_changed = Signal()

    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username
        self.template_service = MonthlyTemplateService(username)
        self.materialization_service = (
            MonthlyTemplateMaterializationService(username)
        )
        self.account_service = BalanceAccountService(username)

        self.accounts = []
        self.current_filter = "all"

        self._montar_interface()
        self._carregar_dados()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Modelos Mensais")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Todos", "all")
        self.filter_combo.addItem("Entradas", "income")
        self.filter_combo.addItem("Saídas", "commitment")
        self.filter_combo.setFixedWidth(160)
        self.filter_combo.currentIndexChanged.connect(
            self._alterar_filtro
        )

        novo = QPushButton("+ Novo modelo")
        novo.clicked.connect(
            self._abrir_dialog_novo_template
        )

        materializar = QPushButton("Materializar mês")
        materializar.clicked.connect(
            self._materializar_mes
        )

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(QLabel("Filtro"))
        header.addWidget(self.filter_combo)
        header.addWidget(novo)
        header.addWidget(materializar)

        layout.addLayout(header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)

        layout.addWidget(self.scroll_area, 1)

    def _carregar_dados(self) -> None:
        self.accounts = self.account_service.listar_contas()
        self._carregar_templates()

    def _alterar_filtro(self) -> None:
        self.current_filter = self.filter_combo.currentData()
        self._carregar_templates()

    def _carregar_templates(self) -> None:
        self._limpar_cards()

        templates = self.template_service.listar_todos()

        if self.current_filter != "all":
            templates = [
                template
                for template in templates
                if template["template_type"] == self.current_filter
            ]

        templates.sort(
            key=lambda template: (
                int(template["day_of_month"] or 0),
                template["description"].lower(),
            )
        )

        for template in templates:
            card = self._criar_card_template(template)

            self.cards_layout.insertWidget(
                self.cards_layout.count() - 1,
                card,
            )

    def _limpar_cards(self) -> None:
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _criar_card_template(
            self,
            template: dict,
    ) -> QFrame:
        is_income = template["template_type"] == "income"
        is_active = bool(template["is_active"])

        cor_fundo = "#f0fdf4" if is_income else "#fff1f2"
        cor_borda = "#bbf7d0" if is_income else "#fecdd3"
        cor_titulo = "#15803d" if is_income else "#be123c"
        tipo_texto = "Entrada" if is_income else "Saída"

        if not is_active:
            cor_fundo = "#f8fafc"
            cor_borda = "#e2e8f0"
            cor_titulo = "#64748b"

        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {cor_fundo};
                border: 1px solid {cor_borda};
                border-radius: 16px;
            }}
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        dia = QLabel(f"Dia {int(template['day_of_month']):02d}")
        dia.setFixedWidth(72)
        dia.setAlignment(Qt.AlignCenter)
        dia.setStyleSheet(
            f"""
            QLabel {{
                background-color: white;
                color: {cor_titulo};
                border: 1px solid {cor_borda};
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }}
            """
        )

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        titulo = QLabel(template["description"])
        titulo.setStyleSheet(
            f"""
            QLabel {{
                border: none;
                color: {cor_titulo};
                font-size: 15px;
                font-weight: bold;
            }}
            """
        )

        subtitulo = QLabel(
            f"{tipo_texto} • {self._formatar_moeda(template['estimated_amount_cents'])}"
        )
        subtitulo.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #64748b;
                font-size: 12px;
            }
            """
        )

        conta = self._obter_nome_conta(
            template["account_id"]
        )

        detalhe = QLabel(
            f"Conta: {conta} • "
            f"{'Ativo' if is_active else 'Inativo'}"
        )
        detalhe.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #94a3b8;
                font-size: 11px;
            }
            """
        )

        info_layout.addWidget(titulo)
        info_layout.addWidget(subtitulo)
        info_layout.addWidget(detalhe)

        editar = QPushButton("Editar")
        editar.clicked.connect(
            lambda checked=False, item=template: self._abrir_dialog_editar_template(item)
        )

        alternar = QPushButton(
            "Desativar" if is_active else "Reativar"
        )
        alternar.clicked.connect(
            lambda checked=False, item=template: self._alternar_template(item)
        )

        layout.addWidget(dia)
        layout.addLayout(info_layout, 1)
        layout.addWidget(editar)
        layout.addWidget(alternar)

        return card

    def _abrir_dialog_novo_template(self) -> None:
        dialog = MonthlyTemplateDialog(
            accounts=self.accounts,
            parent=self,
        )

        if dialog.exec() != MonthlyTemplateDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.template_service.criar_template(
                **dados
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao criar modelo",
                str(erro),
            )
            return

        self._carregar_templates()
        self.data_changed.emit()

    def _abrir_dialog_editar_template(
            self,
            template: dict,
    ) -> None:
        dialog = MonthlyTemplateDialog(
            accounts=self.accounts,
            template_data=template,
            parent=self,
        )

        if dialog.exec() != MonthlyTemplateDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.template_service.atualizar_template(
                template_id=template["id"],
                **dados,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao editar modelo",
                str(erro),
            )
            return

        self._carregar_templates()
        self.data_changed.emit()

    def _alternar_template(
            self,
            template: dict,
    ) -> None:
        try:
            if template["is_active"]:
                self.template_service.desativar_template(
                    template["id"]
                )
            else:
                self.template_service.reativar_template(
                    template["id"]
                )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao alterar modelo",
                str(erro),
            )
            return

        self._carregar_templates()
        self.data_changed.emit()

    def _obter_nome_conta(
            self,
            account_id: int | None,
    ) -> str:
        if account_id is None:
            return "Nenhuma"

        for account in self.accounts:
            if account["id"] == account_id:
                return account["name"]

        return "Conta não encontrada"

    def _formatar_moeda(
            self,
            valor_cents: int,
    ) -> str:
        valor = valor_cents / 100
        texto = f"{valor:,.2f}"

        return (
            "R$ "
            + texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _materializar_mes(self) -> None:
        dialog = MonthYearPickerDialog(parent=self)

        if dialog.exec() != MonthYearPickerDialog.Accepted:
            return

        ano, mes = dialog.obter_mes_ano()

        try:
            resultado = self.materialization_service.materializar_mes(
                ano=ano,
                mes=mes,
                respeitar_limite_31_dias=False,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao materializar mês",
                str(erro),
            )
            return

        QMessageBox.information(
            self,
            "Materialização concluída",
            (
                f"Mês materializado: {mes:02d}/{ano}\n\n"
                f"Receitas criadas: {resultado['receitas_criadas']}\n"
                f"Compromissos criados: {resultado['compromissos_criados']}\n"
                f"Ignorados: {resultado['ignorados']}\n"
                f"Bloqueados pelo limite de 31 dias: "
                f"{resultado['bloqueados_por_limite']}"
            ),
        )

        self.data_changed.emit()


class MonthYearPickerDialog(QDialog):
    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        hoje = date.today()

        self.setWindowTitle("Selecionar mês")
        self.resize(320, 180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        titulo = QLabel("Escolha o mês para materializar")
        titulo.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #0f172a;"
        )

        self.month_combo = QComboBox()
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro",
        ]

        for index, nome_mes in enumerate(meses, start=1):
            self.month_combo.addItem(nome_mes, index)

        self.month_combo.setCurrentIndex(hoje.month - 1)

        self.year_input = QSpinBox()
        self.year_input.setMinimum(2000)
        self.year_input.setMaximum(2100)
        self.year_input.setValue(hoje.year)

        layout.addWidget(titulo)
        layout.addWidget(QLabel("Mês"))
        layout.addWidget(self.month_combo)
        layout.addWidget(QLabel("Ano"))
        layout.addWidget(self.year_input)

        footer = QHBoxLayout()
        footer.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        confirmar = QPushButton("Materializar")
        confirmar.clicked.connect(self.accept)

        footer.addWidget(cancelar)
        footer.addWidget(confirmar)

        layout.addStretch()
        layout.addLayout(footer)

    def obter_mes_ano(self) -> tuple[int, int]:
        return (
            self.year_input.value(),
            self.month_combo.currentData(),
        )

class MonthlyTemplateDialog(QDialog):
    def __init__(
            self,
            accounts: list[dict],
            template_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = accounts
        self.template_data = template_data

        self.setWindowTitle(
            "Editar modelo mensal"
            if template_data
            else "Novo modelo mensal"
        )
        self.resize(460, 420)

        self._montar_interface()

        if self.template_data:
            self._preencher_dados()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        titulo = QLabel(
            "Modelo Mensal"
        )
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        layout.addWidget(titulo)

        tipo_layout = QHBoxLayout()

        self.entrada_radio = QRadioButton("Entrada")
        self.saida_radio = QRadioButton("Saída")
        self.saida_radio.setChecked(True)

        self.tipo_group = QButtonGroup(self)
        self.tipo_group.addButton(self.entrada_radio)
        self.tipo_group.addButton(self.saida_radio)

        tipo_layout.addWidget(self.entrada_radio)
        tipo_layout.addWidget(self.saida_radio)
        tipo_layout.addStretch()

        self.entrada_radio.toggled.connect(
            self._atualizar_estado_conta
        )

        layout.addLayout(tipo_layout)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(
            "Descrição. Ex: Salário, Internet, Luz..."
        )

        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(self.description_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(9999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("R$ ")
        self.amount_input.setSingleStep(10)

        layout.addWidget(QLabel("Valor estimado"))
        layout.addWidget(self.amount_input)

        self.day_input = QSpinBox()
        self.day_input.setMinimum(1)
        self.day_input.setMaximum(31)
        self.day_input.setValue(5)

        layout.addWidget(QLabel("Dia do mês"))
        layout.addWidget(self.day_input)

        self.account_combo = QComboBox()
        self.account_combo.addItem("Nenhuma", None)

        for account in self.accounts:
            self.account_combo.addItem(
                account["name"],
                account["id"],
            )

        layout.addWidget(QLabel("Conta"))
        layout.addWidget(self.account_combo)

        self.auto_materialize_check = QCheckBox(
            "Materializar automaticamente"
        )
        self.auto_materialize_check.setChecked(True)

        layout.addWidget(self.auto_materialize_check)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Observações")

        layout.addWidget(QLabel("Observações"))
        layout.addWidget(self.notes_input)

        footer = QHBoxLayout()
        footer.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self._salvar)

        footer.addWidget(cancelar)
        footer.addWidget(salvar)

        layout.addStretch()
        layout.addLayout(footer)

        self._atualizar_estado_conta()

    def _preencher_dados(self) -> None:
        if self.template_data["template_type"] == "income":
            self.entrada_radio.setChecked(True)
        else:
            self.saida_radio.setChecked(True)

        self.description_input.setText(
            self.template_data["description"]
        )

        self.amount_input.setValue(
            (self.template_data["estimated_amount_cents"] or 0) / 100
        )

        self.day_input.setValue(
            int(self.template_data["day_of_month"] or 1)
        )

        account_id = self.template_data["account_id"]

        for index in range(self.account_combo.count()):
            if self.account_combo.itemData(index) == account_id:
                self.account_combo.setCurrentIndex(index)
                break

        self.auto_materialize_check.setChecked(
            bool(self.template_data["auto_materialize"])
        )

        self.notes_input.setText(
            self.template_data["notes"] or ""
        )

        self._atualizar_estado_conta()

    def _atualizar_estado_conta(self) -> None:
        if self.entrada_radio.isChecked():
            self.account_combo.setEnabled(True)
            return

        self.account_combo.setEnabled(True)

    def _salvar(self) -> None:
        if self.entrada_radio.isChecked():
            if self.account_combo.currentData() is None:
                QMessageBox.warning(
                    self,
                    "Conta obrigatória",
                    "Entradas precisam de uma conta financeira.",
                )
                return

        self.accept()

    def obter_dados(self) -> dict:
        template_type = (
            "income"
            if self.entrada_radio.isChecked()
            else "commitment"
        )

        return {
            "template_type": template_type,
            "description": self.description_input.text(),
            "estimated_amount_cents": int(
                round(self.amount_input.value() * 100)
            ),
            "day_of_month": self.day_input.value(),
            "account_id": self.account_combo.currentData(),
            "category_id": None,
            "payment_type": "bank_account",
            "credit_card_id": None,
            "start_date": None,
            "end_date": None,
            "auto_materialize": self.auto_materialize_check.isChecked(),
            "notes": self.notes_input.text(),
        }