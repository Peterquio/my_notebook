from datetime import date

from dateutil.relativedelta import relativedelta
from PySide6.QtCore import Qt, QDate
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
    QCalendarWidget,
    QDialog,
)

from modules.finance.services.balance_service import BalanceService
from modules.finance.services.balance_account_service import BalanceAccountService
from modules.finance.ui.dialogs.balance_income_dialog import BalanceIncomeDialog
from modules.finance.ui.dialogs.balance_receive_income_dialog import (
    BalanceReceiveIncomeDialog,
)
from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
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

        self.settings_repository = FinanceSettingsRepository(
            self.username
        )

        self.accounts = []

        self.start_date_iso = None
        self.end_date_iso = None

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

        self.periodo_label = QLabel()
        self.periodo_label.setStyleSheet(
            "font-size: 12px; color: #475569;"
        )

        periodo_inicio = QPushButton("Início")
        periodo_inicio.clicked.connect(
            lambda: self._abrir_calendario_periodo("inicio")
        )

        periodo_fim = QPushButton("Fim")
        periodo_fim.clicked.connect(
            lambda: self._abrir_calendario_periodo("fim")
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
        header.addWidget(self.periodo_label)
        header.addWidget(periodo_inicio)
        header.addWidget(periodo_fim)
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

        inicio, fim = self._obter_periodo_padrao()

        self.start_date_iso = inicio
        self.end_date_iso = fim

        self._carregar_receitas()

    def _carregar_receitas(self) -> None:
        if not self.start_date_iso or not self.end_date_iso:
            self.table.setRowCount(0)
            return

        self.periodo_label.setText(
            f"{self._formatar_data(self.start_date_iso)}"
            f" → "
            f"{self._formatar_data(self.end_date_iso)}"
        )

        receitas = self.balance_service.repository.listar_receitas_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
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

    def _abrir_calendario_periodo(
            self,
            campo: str,
    ) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(
            "Selecionar data inicial"
            if campo == "inicio"
            else "Selecionar data final"
        )
        dialog.setModal(True)
        dialog.setMinimumWidth(320)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        calendario = QCalendarWidget()
        calendario.setGridVisible(True)

        data_atual = (
            self.start_date_iso
            if campo == "inicio"
            else self.end_date_iso
        )

        if data_atual is not None:
            calendario.setSelectedDate(
                QDate.fromString(
                    data_atual,
                    "yyyy-MM-dd",
                )
            )

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(dialog.reject)

        aplicar = QPushButton("Aplicar")
        aplicar.clicked.connect(dialog.accept)

        botoes.addWidget(cancelar)
        botoes.addWidget(aplicar)

        layout.addWidget(calendario)
        layout.addLayout(botoes)

        if dialog.exec() != QDialog.Accepted:
            return

        nova_data = calendario.selectedDate().toPython().isoformat()

        if campo == "inicio":
            self.start_date_iso = nova_data
        else:
            self.end_date_iso = nova_data

        self._carregar_receitas()

    def _obter_periodo_padrao(self) -> tuple[str, str]:
        reference_day = (
            self.settings_repository.obter_reference_day()
        )

        hoje = date.today()

        if hoje.day >= reference_day:
            inicio = hoje.replace(
                day=reference_day
            )
        else:
            inicio = (
                    hoje.replace(day=1)
                    + relativedelta(months=-1)
            )

            ultimo_dia = (
                    inicio
                    + relativedelta(day=31)
            ).day

            inicio = inicio.replace(
                day=min(
                    reference_day,
                    ultimo_dia,
                )
            )

        fim = (
                inicio
                + relativedelta(months=1)
                + relativedelta(days=-1)
        )

        return (
            inicio.isoformat(),
            fim.isoformat(),
        )

