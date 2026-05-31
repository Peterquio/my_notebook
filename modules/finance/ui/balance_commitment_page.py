from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.balance_service import BalanceService
from modules.finance.services.balance_account_service import BalanceAccountService
from modules.finance.ui.dialogs.balance_commitment_dialog import (
    BalanceCommitmentDialog,
)
from modules.finance.ui.dialogs.balance_pay_commitment_dialog import (
    BalancePayCommitmentDialog,
)


class BalanceCommitmentPage(QWidget):
    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username

        self.balance_service = BalanceService(self.username)
        self.account_service = BalanceAccountService(self.username)

        self.cycles = []
        self.accounts = []
        self.selected_cycle_id = None

        self._montar_interface()
        self._carregar_dados_base()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Compromissos")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        self.cycle_combo = QComboBox()
        self.cycle_combo.setFixedWidth(260)
        self.cycle_combo.currentIndexChanged.connect(
            self._alterar_ciclo
        )

        novo = QPushButton("+ Novo Compromisso")
        novo.clicked.connect(self._abrir_dialog_novo_compromisso)

        editar = QPushButton("Editar")
        editar.clicked.connect(self._editar_compromisso_selecionado)

        excluir = QPushButton("Excluir")
        excluir.clicked.connect(self._excluir_compromisso_selecionado)

        pagar = QPushButton("Pagar")
        pagar.clicked.connect(self._pagar_compromisso_selecionado)

        reabrir = QPushButton("Reabrir")
        reabrir.clicked.connect(self._reabrir_compromisso_selecionado)

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(QLabel("Ciclo"))
        header.addWidget(self.cycle_combo)
        header.addWidget(novo)
        header.addWidget(editar)
        header.addWidget(excluir)
        header.addWidget(pagar)
        header.addWidget(reabrir)

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "VENCIMENTO",
                "CONTA",
                "DESCRIÇÃO",
                "TIPO",
                "VALOR",
                "STATUS",
            ]
        )

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header_table = self.table.horizontalHeader()
        header_table.setSectionResizeMode(0, QHeaderView.Fixed)
        header_table.setSectionResizeMode(1, QHeaderView.Fixed)
        header_table.setSectionResizeMode(2, QHeaderView.Stretch)
        header_table.setSectionResizeMode(3, QHeaderView.Fixed)
        header_table.setSectionResizeMode(4, QHeaderView.Fixed)
        header_table.setSectionResizeMode(5, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 110)

        layout.addWidget(self.table, 1)

    def _carregar_dados_base(self) -> None:
        self.accounts = self.account_service.listar_contas()
        self.cycles = self.balance_service.listar_ciclos()

        self.cycle_combo.blockSignals(True)
        self.cycle_combo.clear()

        if not self.cycles:
            self.cycle_combo.addItem("Nenhum ciclo encontrado", None)
            self.selected_cycle_id = None
            self.cycle_combo.blockSignals(False)
            self._carregar_compromissos()
            return

        for ciclo in self.cycles:
            texto = (
                f"{self._formatar_data(ciclo['start_date'])}"
                f" → "
                f"{self._formatar_data(ciclo['end_date'])}"
            )

            self.cycle_combo.addItem(
                texto,
                ciclo["id"],
            )

        self.selected_cycle_id = self.cycle_combo.currentData()
        self.cycle_combo.blockSignals(False)

        self._carregar_compromissos()

    def _alterar_ciclo(self) -> None:
        self.selected_cycle_id = self.cycle_combo.currentData()
        self._carregar_compromissos()

    def _carregar_compromissos(self) -> None:
        if self.selected_cycle_id is None:
            self.table.setRowCount(0)
            return

        compromissos = self.balance_service.listar_compromissos_ciclo(
            self.selected_cycle_id
        )

        account_by_id = {
            account["id"]: account
            for account in self.accounts
        }

        self.table.setRowCount(len(compromissos))

        for row_index, compromisso in enumerate(compromissos):
            self._adicionar_compromisso_na_tabela(
                row_index=row_index,
                compromisso=compromisso,
                account_by_id=account_by_id,
            )

    def _adicionar_compromisso_na_tabela(
            self,
            row_index: int,
            compromisso: dict,
            account_by_id: dict,
    ) -> None:
        conta = account_by_id.get(
            compromisso["account_id"]
        )

        conta_nome = conta["name"] if conta else "Conta não encontrada"

        tipo_nome = {
            "bank_account": "Conta",
            "credit_card": "Cartão",
        }.get(
            compromisso["payment_type"],
            compromisso["payment_type"],
        )

        status_nome = {
            "expected": "Previsto",
            "paid": "Pago",
        }.get(
            compromisso["status"],
            compromisso["status"],
        )

        valores = [
            self._formatar_data(compromisso["due_date"]),
            conta_nome,
            compromisso["description"],
            tipo_nome,
            self._formatar_moeda(compromisso["expected_amount_cents"]),
            status_nome,
        ]

        for col_index, valor in enumerate(valores):
            item = QTableWidgetItem(valor)
            item.setData(Qt.UserRole, compromisso)

            if col_index in [0, 3, 4, 5]:
                item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(
                row_index,
                col_index,
                item,
            )

        self.table.setRowHeight(row_index, 34)

    def _obter_compromisso_selecionado(self) -> dict | None:
        selected_items = self.table.selectedItems()

        if not selected_items:
            return None

        row = selected_items[0].row()
        item = self.table.item(row, 0)

        if item is None:
            return None

        return item.data(Qt.UserRole)

    def _abrir_dialog_novo_compromisso(self) -> None:
        if self.selected_cycle_id is None:
            QMessageBox.warning(
                self,
                "Ciclo obrigatório",
                "Crie ou selecione um ciclo antes de cadastrar compromissos.",
            )
            return

        if not self.accounts:
            QMessageBox.warning(
                self,
                "Conta obrigatória",
                "Cadastre uma conta financeira antes de criar compromissos.",
            )
            return

        dialog = BalanceCommitmentDialog(
            accounts=self.accounts,
            parent=self,
        )

        if dialog.exec() != BalanceCommitmentDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.balance_service.criar_compromisso(
            cycle_id=self.selected_cycle_id,
            **dados,
        )

        self._carregar_compromissos()

    def _editar_compromisso_selecionado(self) -> None:
        compromisso = self._obter_compromisso_selecionado()

        if compromisso is None:
            QMessageBox.information(
                self,
                "Selecione um compromisso",
                "Selecione um compromisso para editar.",
            )
            return

        if compromisso["status"] != "expected":
            QMessageBox.warning(
                self,
                "Compromisso já pago",
                "Compromissos pagos não podem ser editados. Reabra o compromisso primeiro.",
            )
            return

        if compromisso["payment_type"] == "credit_card":
            QMessageBox.warning(
                self,
                "Compromisso de cartão",
                "Compromissos gerados por cartão devem ser editados no módulo de cartão.",
            )
            return

        dialog = BalanceCommitmentDialog(
            accounts=self.accounts,
            commitment_data=compromisso,
            parent=self,
        )

        if dialog.exec() != BalanceCommitmentDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.balance_service.atualizar_compromisso(
            compromisso_id=compromisso["id"],
            **dados,
        )

        self._carregar_compromissos()

    def _excluir_compromisso_selecionado(self) -> None:
        compromisso = self._obter_compromisso_selecionado()

        if compromisso is None:
            QMessageBox.information(
                self,
                "Selecione um compromisso",
                "Selecione um compromisso para excluir.",
            )
            return

        if compromisso["status"] != "expected":
            QMessageBox.warning(
                self,
                "Compromisso já pago",
                "Compromissos pagos não podem ser excluídos. Reabra o compromisso primeiro.",
            )
            return

        if compromisso["payment_type"] == "credit_card":
            QMessageBox.warning(
                self,
                "Compromisso de cartão",
                "Compromissos gerados por cartão devem ser corrigidos no módulo de cartão.",
            )
            return

        resposta = QMessageBox.question(
            self,
            "Excluir compromisso",
            f"Deseja excluir o compromisso '{compromisso['description']}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        self.balance_service.excluir_compromisso(
            compromisso["id"]
        )

        self._carregar_compromissos()

    def _pagar_compromisso_selecionado(self) -> None:
        compromisso = self._obter_compromisso_selecionado()

        if compromisso is None:
            QMessageBox.information(
                self,
                "Selecione um compromisso",
                "Selecione um compromisso para pagar.",
            )
            return

        if compromisso["status"] != "expected":
            QMessageBox.warning(
                self,
                "Compromisso já pago",
                "Este compromisso já foi pago.",
            )
            return

        dialog = BalancePayCommitmentDialog(
            commitment_data=compromisso,
            parent=self,
        )

        if dialog.exec() != BalancePayCommitmentDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.balance_service.pagar_compromisso(
            compromisso_id=compromisso["id"],
            **dados,
        )

        self._carregar_compromissos()

    def _reabrir_compromisso_selecionado(self) -> None:
        compromisso = self._obter_compromisso_selecionado()

        if compromisso is None:
            QMessageBox.information(
                self,
                "Selecione um compromisso",
                "Selecione um compromisso para reabrir.",
            )
            return

        if compromisso["status"] != "paid":
            QMessageBox.warning(
                self,
                "Compromisso ainda previsto",
                "Apenas compromissos pagos podem ser reabertos.",
            )
            return

        self.balance_service.reabrir_compromisso(
            compromisso["id"]
        )

        self._carregar_compromissos()

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

    def _formatar_data(
            self,
            data_iso: str,
    ) -> str:
        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"