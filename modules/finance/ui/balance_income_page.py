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
from modules.finance.ui.dialogs.balance_income_dialog import BalanceIncomeDialog
from modules.finance.ui.dialogs.balance_receive_income_dialog import (
    BalanceReceiveIncomeDialog,
)


class BalanceIncomePage(QWidget):
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

        titulo = QLabel("Receitas")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        self.cycle_combo = QComboBox()
        self.cycle_combo.setFixedWidth(260)
        self.cycle_combo.currentIndexChanged.connect(
            self._alterar_ciclo
        )

        nova = QPushButton("+ Nova Receita")
        nova.clicked.connect(self._abrir_dialog_nova_receita)

        editar = QPushButton("Editar")
        editar.clicked.connect(self._editar_receita_selecionada)

        excluir = QPushButton("Excluir")
        excluir.clicked.connect(self._excluir_receita_selecionada)

        receber = QPushButton("Receber")
        receber.clicked.connect(self._receber_receita_selecionada)

        reabrir = QPushButton("Reabrir")
        reabrir.clicked.connect(self._reabrir_receita_selecionada)

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(QLabel("Ciclo"))
        header.addWidget(self.cycle_combo)
        header.addWidget(nova)
        header.addWidget(editar)
        header.addWidget(excluir)
        header.addWidget(receber)
        header.addWidget(reabrir)

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                "DATA PREVISTA",
                "CONTA",
                "DESCRIÇÃO",
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

        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 110)

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
            self._carregar_receitas()
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

        self._carregar_receitas()

    def _alterar_ciclo(self) -> None:
        self.selected_cycle_id = self.cycle_combo.currentData()
        self._carregar_receitas()

    def _carregar_receitas(self) -> None:
        if self.selected_cycle_id is None:
            self.table.setRowCount(0)
            return

        receitas = self.balance_service.listar_receitas_ciclo(
            self.selected_cycle_id
        )

        account_by_id = {
            account["id"]: account
            for account in self.accounts
        }

        self.table.setRowCount(len(receitas))

        for row_index, receita in enumerate(receitas):
            self._adicionar_receita_na_tabela(
                row_index=row_index,
                receita=receita,
                account_by_id=account_by_id,
            )

    def _adicionar_receita_na_tabela(
            self,
            row_index: int,
            receita: dict,
            account_by_id: dict,
    ) -> None:
        conta = account_by_id.get(
            receita["account_id"]
        )

        conta_nome = conta["name"] if conta else "Conta não encontrada"

        status_nome = {
            "expected": "Prevista",
            "received": "Recebida",
        }.get(
            receita["status"],
            receita["status"],
        )

        valores = [
            self._formatar_data(receita["expected_date"]),
            conta_nome,
            receita["description"],
            self._formatar_moeda(receita["expected_amount_cents"]),
            status_nome,
        ]

        for col_index, valor in enumerate(valores):
            item = QTableWidgetItem(valor)
            item.setData(Qt.UserRole, receita)

            if col_index in [0, 3, 4]:
                item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(
                row_index,
                col_index,
                item,
            )

        self.table.setRowHeight(row_index, 34)

    def _obter_receita_selecionada(self) -> dict | None:
        selected_items = self.table.selectedItems()

        if not selected_items:
            return None

        row = selected_items[0].row()
        item = self.table.item(row, 0)

        if item is None:
            return None

        return item.data(Qt.UserRole)

    def _abrir_dialog_nova_receita(self) -> None:
        if self.selected_cycle_id is None:
            QMessageBox.warning(
                self,
                "Ciclo obrigatório",
                "Crie ou selecione um ciclo antes de cadastrar receitas.",
            )
            return

        if not self.accounts:
            QMessageBox.warning(
                self,
                "Conta obrigatória",
                "Cadastre uma conta financeira antes de criar receitas.",
            )
            return

        dialog = BalanceIncomeDialog(
            accounts=self.accounts,
            parent=self,
        )

        if dialog.exec() != BalanceIncomeDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.balance_service.criar_receita(
            cycle_id=self.selected_cycle_id,
            **dados,
        )

        self._carregar_receitas()

    def _editar_receita_selecionada(self) -> None:
        receita = self._obter_receita_selecionada()

        if receita is None:
            QMessageBox.information(
                self,
                "Selecione uma receita",
                "Selecione uma receita para editar.",
            )
            return

        if receita["status"] != "expected":
            QMessageBox.warning(
                self,
                "Receita já recebida",
                "Receitas recebidas não podem ser editadas. Reabra a receita primeiro.",
            )
            return

        dialog = BalanceIncomeDialog(
            accounts=self.accounts,
            income_data=receita,
            parent=self,
        )

        if dialog.exec() != BalanceIncomeDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.balance_service.atualizar_receita(
            receita_id=receita["id"],
            **dados,
        )

        self._carregar_receitas()

    def _excluir_receita_selecionada(self) -> None:
        receita = self._obter_receita_selecionada()

        if receita is None:
            QMessageBox.information(
                self,
                "Selecione uma receita",
                "Selecione uma receita para excluir.",
            )
            return

        if receita["status"] != "expected":
            QMessageBox.warning(
                self,
                "Receita já recebida",
                "Receitas recebidas não podem ser excluídas. Reabra a receita primeiro.",
            )
            return

        resposta = QMessageBox.question(
            self,
            "Excluir receita",
            f"Deseja excluir a receita '{receita['description']}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        self.balance_service.excluir_receita(
            receita["id"]
        )

        self._carregar_receitas()

    def _receber_receita_selecionada(self) -> None:
        receita = self._obter_receita_selecionada()

        if receita is None:
            QMessageBox.information(
                self,
                "Selecione uma receita",
                "Selecione uma receita para receber.",
            )
            return

        if receita["status"] != "expected":
            QMessageBox.warning(
                self,
                "Receita já recebida",
                "Esta receita já foi recebida.",
            )
            return

        dialog = BalanceReceiveIncomeDialog(
            income_data=receita,
            parent=self,
        )

        if dialog.exec() != BalanceReceiveIncomeDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.balance_service.receber_receita(
            receita_id=receita["id"],
            **dados,
        )

        self._carregar_receitas()

    def _reabrir_receita_selecionada(self) -> None:
        receita = self._obter_receita_selecionada()

        if receita is None:
            QMessageBox.information(
                self,
                "Selecione uma receita",
                "Selecione uma receita para reabrir.",
            )
            return

        if receita["status"] != "received":
            QMessageBox.warning(
                self,
                "Receita ainda prevista",
                "Apenas receitas recebidas podem ser reabertas.",
            )
            return

        self.balance_service.reabrir_receita(
            receita["id"]
        )

        self._carregar_receitas()

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