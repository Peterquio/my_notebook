from PySide6.QtCore import Qt, Signal
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

from modules.finance.services.balance_account_service import (
    BalanceAccountService,
)

from modules.finance.ui.dialogs.bank_account_setup_dialog import (
    BankAccountSetupDialog,
)

from modules.finance.services.balance_service import (
    BalanceService,
)

class BalanceAccountsPage(QWidget):
    data_changed = Signal()

    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username
        self.account_service = BalanceAccountService(self.username)
        self.balance_service = BalanceService(self.username)

        self.cycles = []
        self.selected_cycle_id = None

        self._montar_interface()
        self._carregar_dados_base()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Contas Financeiras")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        self.cycle_combo = QComboBox()
        self.cycle_combo.setFixedWidth(260)
        self.cycle_combo.currentIndexChanged.connect(
            self._alterar_ciclo
        )

        nova_conta = QPushButton("+ Nova conta")
        nova_conta.clicked.connect(
            self._abrir_dialog_nova_conta
        )

        editar = QPushButton("Editar")
        editar.clicked.connect(
            self._editar_conta_selecionada
        )

        desativar = QPushButton("Desativar")
        desativar.clicked.connect(
            self._desativar_conta_selecionada
        )

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(QLabel("Ciclo"))
        header.addWidget(self.cycle_combo)
        header.addWidget(nova_conta)
        header.addWidget(editar)
        header.addWidget(desativar)

        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "CONTA",
                "BANCO",
                "AGÊNCIA",
                "Nº CONTA",
                "TIPO",
                "SALDO INICIAL",
                "GLOBAL",
            ]
        )

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        header_table = self.table.horizontalHeader()
        header_table.setSectionResizeMode(0, QHeaderView.Stretch)
        header_table.setSectionResizeMode(1, QHeaderView.Fixed)
        header_table.setSectionResizeMode(2, QHeaderView.Fixed)
        header_table.setSectionResizeMode(3, QHeaderView.Fixed)
        header_table.setSectionResizeMode(4, QHeaderView.Fixed)
        header_table.setSectionResizeMode(5, QHeaderView.Fixed)
        header_table.setSectionResizeMode(6, QHeaderView.Fixed)

        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 80)

        layout.addWidget(self.table, 1)

    def _carregar_dados_base(self) -> None:
        self.cycles = self.balance_service.listar_ciclos()

        self.cycle_combo.blockSignals(True)
        self.cycle_combo.clear()

        if not self.cycles:
            self.cycle_combo.addItem("Nenhum ciclo encontrado", None)
            self.selected_cycle_id = None
            self.cycle_combo.blockSignals(False)
            self._carregar_contas()
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

        self._carregar_contas()

    def _alterar_ciclo(self) -> None:
        self.selected_cycle_id = self.cycle_combo.currentData()
        self._carregar_contas()

    def _carregar_contas(self) -> None:
        contas = self.account_service.listar_contas()

        self.table.setRowCount(len(contas))

        for row_index, conta in enumerate(contas):
            self._adicionar_conta_na_tabela(
                row_index=row_index,
                conta=conta,
            )

    def _adicionar_conta_na_tabela(
            self,
            row_index: int,
            conta: dict,
    ) -> None:
        tipo_nome = {
            "bank": "Banco",
            "wallet": "Carteira",
            "cash": "Dinheiro",
        }.get(
            conta["account_type"],
            conta["account_type"],
        )

        saldo_inicial = self.account_service.buscar_saldo_inicial_conta(
            cycle_id=self.selected_cycle_id,
            account_id=conta["id"],
        ) if self.selected_cycle_id is not None else 0

        valores = [
            conta["name"],
            conta.get("institution_name") or "-",
            conta.get("agency") or "-",
            conta.get("account_number") or "-",
            tipo_nome,
            self._formatar_moeda(saldo_inicial),
            "Sim" if conta["include_in_global_balance"] else "Não",
        ]

        for col_index, valor in enumerate(valores):
            item = QTableWidgetItem(valor)
            item.setData(Qt.UserRole, conta)

            if col_index in [2, 4, 5, 6]:
                item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(
                row_index,
                col_index,
                item,
            )

        self.table.setRowHeight(row_index, 34)

    def _obter_conta_selecionada(self) -> dict | None:
        selected_items = self.table.selectedItems()

        if not selected_items:
            return None

        row = selected_items[0].row()
        item = self.table.item(row, 0)

        if item is None:
            return None

        return item.data(Qt.UserRole)

    def _abrir_dialog_nova_conta(self) -> None:
        dialog = BankAccountSetupDialog(parent=self)

        if dialog.exec() != BankAccountSetupDialog.Accepted:
            return

        dados = dialog.obter_dados()

        account_id = self.account_service.criar_conta(
            **dados
        )

        opening_balance_cents = dados.get(
            "opening_balance_cents",
            0,
        )

        self._definir_saldo_inicial_conta(
            account_id=account_id,
            opening_balance_cents=opening_balance_cents,
        )
        self._carregar_contas()
        self.data_changed.emit()

    def _definir_saldo_inicial_conta(
            self,
            account_id: int,
            opening_balance_cents: int,
    ) -> None:

        if not self.cycles:
            return

        primeiro_ciclo = sorted(
            self.cycles,
            key=lambda ciclo: ciclo["start_date"],
        )[0]

        self.account_service.definir_saldo_inicial_conta(
            cycle_id=primeiro_ciclo["id"],
            account_id=account_id,
            opening_balance_cents=opening_balance_cents,
        )

    def _editar_conta_selecionada(self) -> None:
        conta = self._obter_conta_selecionada()

        if conta is None:
            QMessageBox.information(
                self,
                "Selecione uma conta",
                "Selecione uma conta para editar.",
            )
            return

        saldo_inicial_cents = 0

        if self.selected_cycle_id is not None:
            saldo_inicial_cents = self.account_service.buscar_saldo_inicial_conta(
                cycle_id=self.selected_cycle_id,
                account_id=conta["id"],
            )

        conta_para_edicao = dict(conta)
        conta_para_edicao["opening_balance_cents"] = saldo_inicial_cents

        dialog = BankAccountSetupDialog(
            account_data=conta_para_edicao,
            parent=self,
        )

        if dialog.exec() != BankAccountSetupDialog.Accepted:
            return

        dados = dialog.obter_dados()

        opening_balance_cents = dados.pop(
            "opening_balance_cents",
            None,
        )

        self.account_service.atualizar_conta(
            account_id=conta["id"],
            **dados,
        )

        if opening_balance_cents is not None:
            self._definir_saldo_inicial_conta(
                account_id=conta["id"],
                opening_balance_cents=opening_balance_cents,
            )

        self._carregar_contas()
        self.data_changed.emit()

    def _desativar_conta_selecionada(self) -> None:
        conta = self._obter_conta_selecionada()

        if conta is None:
            QMessageBox.information(
                self,
                "Selecione uma conta",
                "Selecione uma conta para desativar.",
            )
            return

        resposta = QMessageBox.question(
            self,
            "Desativar conta",
            f"Deseja desativar a conta '{conta['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        self.account_service.desativar_conta(
            conta["id"]
        )

        self._carregar_contas()
        self.data_changed.emit()

    def _formatar_data(
            self,
            data_iso: str,
    ) -> str:
        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"

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