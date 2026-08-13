from datetime import date
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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
                "SALDO ATUAL",
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

        saldo_atual = self.balance_service.calcular_saldo_conta_na_data(
            account_id=conta["id"],
            data_iso=date.today().isoformat(),
        )

        valores = [
            conta["name"],
            conta.get("institution_name") or "-",
            conta.get("agency") or "-",
            conta.get("account_number") or "-",
            tipo_nome,
            self._formatar_moeda(saldo_atual),
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

        self.account_service.criar_conta(
            **dados
        )

        self._carregar_contas()
        self.data_changed.emit()

    def _editar_conta_selecionada(self) -> None:
        conta = self._obter_conta_selecionada()

        if conta is None:
            QMessageBox.information(
                self,
                "Selecione uma conta",
                "Selecione uma conta para editar.",
            )
            return

        conta_para_edicao = dict(conta)

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