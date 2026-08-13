from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QFrame, QLabel,
    QPushButton, QLineEdit,
    QComboBox, QHBoxLayout,
    QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView,
    QGridLayout,  QSizePolicy,
)

from modules.finance.services.importers.credit_card_import_service import (
    CreditCardImportService,
)

from modules.finance.services.credit_card_detail_service import (
    CreditCardDetailService,
)

from modules.finance.ui.dialogs.credit_card_import_preview_dialog import (
    CreditCardImportPreviewDialog,
)

from modules.finance.services.finance_category_service import (
    FinanceCategoryService,
)

from modules.finance.services.credit_card_portable_data_service import (
    CreditCardPortableDataService,
)

from modules.finance.ui.dialogs.credit_card_expense_dialog import (
    CreditCardExpenseDialog,
)

from modules.finance.ui.dialogs.credit_card_previous_payment_dialog import (
    CreditCardPreviousPaymentDialog,
)

from modules.finance.services.credit_card_balance_sync_service import (
    CreditCardBalanceSyncService,
)

from modules.finance.services.balance_account_service import (
    BalanceAccountService,
)

from modules.finance.services.credit_card_account_link_service import (
    CreditCardAccountLinkService,
)

from modules.finance.ui.dialogs.credit_card_account_link_dialog import (
    CreditCardAccountLinkDialog,
)

class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

class CreditCardInvoicePage(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(
            self,
            credit_card: dict,
            username: str,
            invoice_year: int | None = None,
            invoice_month: int | None = None,
            sort_mode: str = "parcelas",
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.credit_card = credit_card
        self.username = username
        self.selected_invoice_year = invoice_year
        self.selected_invoice_month = invoice_month

        self.import_service = CreditCardImportService(self.username)
        self.detail_service = CreditCardDetailService(username=self.username)

        self.balance_sync_service = (
            CreditCardBalanceSyncService(
                self.username
            )
        )

        self.balance_account_service = BalanceAccountService(
            self.username
        )

        self.account_link_service = CreditCardAccountLinkService(
            self.username
        )

        self.portable_data_service = CreditCardPortableDataService(
            self.username
        )

        self.category_service = FinanceCategoryService(
            self.username
        )

        self.categories = self.category_service.listar_categorias_ativas()
        self.sort_mode = sort_mode

        self.invoice_data = self._carregar_fatura_selecionada()

        self._montar_interface()

    def _montar_interface(self) -> QWidget:
        self.content_layout = QVBoxLayout(self)

        layout = self.content_layout
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        layout.addLayout(
            self._criar_header()
        )

        layout.addLayout(
            self._criar_cards_resumo()
        )

        layout.addLayout(
            self._criar_filtros()
        )

        self.table = self._criar_tabela()
        layout.addWidget(self.table, 1)

    def _carregar_fatura_selecionada(self) -> dict:
        if (
                self.selected_invoice_year is not None
                and self.selected_invoice_month is not None
        ):
            return self.detail_service.carregar_fatura_por_mes(
                credit_card=self.credit_card,
                invoice_year=self.selected_invoice_year,
                invoice_month=self.selected_invoice_month,
                sort_mode=self.sort_mode,
            )

        return self.detail_service.carregar_fatura_atual(
            self.credit_card,
            sort_mode=self.sort_mode,
        )

    def _criar_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        titulo_area = QVBoxLayout()
        titulo_area.setSpacing(2)

        titulo = QLabel(
            self.credit_card["name"]
        )
        titulo.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo = QLabel("Cartão de Crédito • Platinum")
        subtitulo.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        titulo_area.addWidget(titulo)
        titulo_area.addWidget(subtitulo)

        atualizado = QLabel(
            "Atualizado em 08/06/2026 às 09:30"
        )
        atualizado.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        layout.addLayout(titulo_area)
        layout.addStretch()
        layout.addWidget(atualizado)

        return layout

    def _criar_cards_resumo(self) -> QGridLayout:
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        cards = self.detail_service.montar_cards_resumo_fatura(
            credit_card=self.credit_card,
            invoice_data=self.invoice_data,
        )

        cards.append(
            {
                "icon": "+",
                "title": "Novo lançamento",
                "value": "Adicionar",
                "subtitle": "Registrar despesa",
                "action": self._abrir_dialog_novo_lancamento,
            }
        )

        total_cards = len(cards)
        columns = 6 if self.width() >= 1050 else 3

        for index, card_data in enumerate(cards):
            row = index // columns
            column = index % columns

            card = self._criar_card_resumo(
                card_data["icon"],
                card_data["title"],
                card_data["value"],
                card_data["subtitle"],
            )

            if "action" in card_data:
                card.setCursor(Qt.PointingHandCursor)
                card.mousePressEvent = (
                    lambda event, action=card_data["action"]: action()
                )
                card.setStyleSheet(
                    """
                    QFrame {
                        background-color: #6d28d9;
                        border: 1px solid #6d28d9;
                        border-radius: 14px;
                    }

                    QFrame:hover {
                        background-color: #5b21b6;
                        border-color: #5b21b6;
                    }
                    """
                )

                for label in card.findChildren(QLabel):
                    label.setStyleSheet(
                        label.styleSheet()
                        .replace("#0f172a", "white")
                        .replace("#64748b", "#ede9fe")
                        .replace("#6d28d9", "white")
                        .replace("#f3e8ff", "#7c3aed")
                    )

            layout.addWidget(
                card,
                row,
                column,
            )

        for column in range(columns):
            layout.setColumnStretch(column, 1)

        return layout

    def _criar_card_resumo(
            self,
            icon: str,
            title: str,
            value: str,
            subtitle: str,
    ) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(56)
        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 7, 12, 7)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(30, 30)
        icon_label.setStyleSheet(
            """
            QLabel {
                background-color: #f3e8ff;
                color: #6d28d9;
                border: none;
                border-radius: 15px;
                font-size: 16px;
            }
            """
        )

        textos = QVBoxLayout()
        textos.setSpacing(1)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "border: none; font-size: 11px; color: #64748b;"
        )

        value_label = QLabel(value)
        value_label.setStyleSheet(
            """
            border: none;
            font-size: 15px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "border: none; font-size: 10px; color: #64748b;"
        )

        textos.addWidget(title_label)
        textos.addWidget(value_label)
        textos.addWidget(subtitle_label)

        layout.addWidget(icon_label)
        layout.addLayout(textos)
        layout.addStretch()

        return card

    def _criar_filtros(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar lançamento...")
        self.busca_input.setFixedWidth(220)
        self.busca_input.textChanged.connect(self._aplicar_filtros_tabela)

        self.categoria_filter_combo = QComboBox()
        self.categoria_filter_combo.addItem("Todas as categorias", None)

        for categoria in self.categories:
            self.categoria_filter_combo.addItem(
                categoria["name"],
                categoria["id"],
            )

        self.categoria_filter_combo.setFixedWidth(180)
        self.categoria_filter_combo.currentIndexChanged.connect(
            self._aplicar_filtros_tabela
        )

        #total_lancamentos = QLabel(
        #    f"{self.invoice_data['total_lancamentos']} lançamentos"
        #)
        #total_lancamentos.setStyleSheet(
        #    "font-size: 12px; color: #64748b;"
        #)

        importar = self._criar_botao_icone(
            texto="⬆",
            tooltip="Importar CSV Nubank",
        )
        importar.clicked.connect(
            self._importar_csv
        )

        importar_backup = self._criar_botao_icone(
            texto="↺",
            tooltip="Importar backup",
        )
        importar_backup.clicked.connect(
            self._importar_dados_cartao
        )

        exportar = self._criar_botao_icone(
            texto="⬇",
            tooltip="Exportar dados",
        )
        exportar.clicked.connect(
            self._exportar_dados_cartao
        )

        vincular_conta = self._criar_botao_icone(
            texto="🏦",
            tooltip="Vincular cartão a uma conta",
        )
        vincular_conta.clicked.connect(
            self._abrir_dialog_vincular_conta
        )

        self.ordenar_combo = QComboBox()
        self.ordenar_combo.addItems(
            [
                "Ordenar por categoria",
                "Ordenar por data",
                "Ordenar por ordem alfabética",
                "Ordenar por valor",
                "Ordenar por parcelas pagas",
            ]
        )
        self.ordenar_combo.setFixedWidth(210)
        sort_index = {
            "categoria": 0,
            "data": 1,
            "alfabetica": 2,
            "valor": 3,
            "parcelas": 4,
        }

        self.ordenar_combo.setCurrentIndex(
            sort_index.get(self.sort_mode, 4)
        )

        self.ordenar_combo.currentIndexChanged.connect(
            self._alterar_ordenacao
        )

        layout.addWidget(self.busca_input)
        layout.addWidget(self.categoria_filter_combo)
        #layout.addWidget(total_lancamentos)
        layout.addStretch()
        layout.addWidget(importar)
        layout.addWidget(importar_backup)
        layout.addWidget(exportar)
        layout.addWidget(vincular_conta)
        layout.addWidget(self.ordenar_combo)

        return layout

    def _criar_botao_icone(
            self,
            texto: str,
            tooltip: str,
    ) -> QPushButton:
        botao = QPushButton(texto)
        botao.setFixedSize(38, 36)
        botao.setToolTip(tooltip)
        botao.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #dbe4f0;
                border-radius: 10px;
                color: #475569;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #f8fafc;
                border-color: #cbd5e1;
            }
            """
        )

        return botao

    def _alterar_ordenacao(
            self,
            index: int,
    ) -> None:
        sort_modes = {
            0: "categoria",
            1: "data",
            2: "alfabetica",
            3: "valor",
            4: "parcelas",
        }

        self.sort_mode = sort_modes.get(
            index,
            "categoria",
        )

        self.invoice_data = self._carregar_fatura_selecionada()

        self._recarregar_tabela()

    def _criar_tabela(self) -> QTableWidget:
        table = QTableWidget()
        table.setStyleSheet(
            """
            QHeaderView::section {
                font-size: 10px;
                font-weight: bold;
                padding-top: 4px;
                padding-bottom: 4px;
            }
            """
        )
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            [
                "DATA",
                "",
                "LANÇAMENTO",
                "CATEGORIA",
                "PARCELAS",
                "VALOR RESTANTE",
                "VALOR NA FATURA",
            ]
        )

        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.cellDoubleClicked.connect(
            self._editar_lancamento_duplo_clique
        )
        table.setAlternatingRowColors(False)

        header = table.horizontalHeader()
        header.setFixedHeight(28)
        header_font = header.font()
        header_font.setPointSize(max(header_font.pointSize() - 2, 8))
        header.setFont(header_font)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 22)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 105)
        table.setColumnWidth(5, 105)
        table.setColumnWidth(6, 135)

        rows = self._dados_mockados()
        table.setRowCount(len(rows))

        for index, row in enumerate(rows):
            if row["type"] == "group":
                self._adicionar_grupo(table, index, row)
            else:
                self._adicionar_lancamento(table, index, row)

        return table

    def _adicionar_grupo(
            self,
            table: QTableWidget,
            row_index: int,
            row: dict,
    ) -> None:
        background = QColor(row["background"])
        color = QColor(row["color"])

        for col in range(table.columnCount()):
            item = QTableWidgetItem("")
            item.setBackground(background)
            item.setFlags(Qt.ItemIsEnabled)
            table.setItem(row_index, col, item)

        nome = QTableWidgetItem(
            f"{row['icon']}  {row['name']}"
        )
        nome.setForeground(color)
        nome.setBackground(background)
        nome.setFont(self._font_bold())
        table.setItem(row_index, 2, nome)

        count = QTableWidgetItem(row["count"])
        count.setTextAlignment(Qt.AlignCenter)
        count.setForeground(QColor("#475569"))
        count.setBackground(background)
        table.setItem(row_index, 5, count)

        total = QTableWidgetItem(row["total"])
        total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total.setForeground(color)
        total.setBackground(background)
        total.setFont(self._font_bold())
        table.setItem(row_index, 6, total)

        table.setRowHeight(row_index, 34)

    def _adicionar_lancamento(
            self,
            table: QTableWidget,
            row_index: int,
            row: dict,
    ) -> None:
        valores = [
            row["date"],
            "",
            row["description"],
            row["category"],
            row["installment"],
            row["remaining"],
            row["amount"],
        ]

        category_color = row.get(
            "category_color",
            "#6d28d9",
        )

        is_last_installment = row.get(
            "is_last_installment",
            False,
        )

        row_background = QColor(226, 232, 240) if is_last_installment else None

        for col, value in enumerate(valores):
            item = QTableWidgetItem(value)
            item.setData(Qt.UserRole, row)
            item.setForeground(QColor("#334155"))

            if row_background is not None:
                item.setBackground(row_background)

            if col == 5:
                fonte = item.font()
                tamanho_atual = fonte.pointSize()

                if tamanho_atual > 0:
                    fonte.setPointSize(max(tamanho_atual - 2, 8))

                item.setFont(fonte)

            if col == 1:
                item.setBackground(
                    QColor(category_color)
                )

            if col in [0, 1, 4]:
                item.setTextAlignment(Qt.AlignCenter)
            elif col in [5, 6]:
                item.setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter
                )
            else:
                item.setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                )

            table.setItem(row_index, col, item)

            if col == 3:
                combo = NoWheelComboBox()
                combo.setStyleSheet(
                    """
                    QComboBox {
                        background-color: white;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        padding: 4px 8px;
                        color: #334155;
                        font-size: 12px;
                    }
                    """
                )

                for categoria in self.categories:
                    combo.addItem(
                        categoria["name"],
                        categoria["id"],
                    )

                category_id = row.get("category_id")

                if category_id is not None:
                    index = combo.findData(category_id)

                    if index >= 0:
                        combo.setCurrentIndex(index)

                combo.currentIndexChanged.connect(
                    lambda _index,
                           expense_id=row.get("expense_id"),
                           combo=combo,
                           row_index=row_index: (
                        self._alterar_categoria_lancamento(
                            expense_id=expense_id,
                            category_id=combo.currentData(),
                            row_index=row_index,
                        )
                    )
                )

                table.setCellWidget(
                    row_index,
                    col,
                    combo,
                )

        table.setRowHeight(row_index, 31)

    def _criar_footer(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        texto = QLabel("Mostrando 1–26 de 26 lançamentos")
        texto.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        pagina = QLabel("1")
        pagina.setAlignment(Qt.AlignCenter)
        pagina.setFixedSize(30, 30)
        pagina.setStyleSheet(
            """
            background-color: #6d28d9;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            """
        )

        itens = QLabel(
            f"{self.invoice_data['total_lancamentos']} lançamentos"
        )
        itens.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        layout.addWidget(texto)
        layout.addStretch()
        layout.addWidget(pagina)
        layout.addStretch()
        layout.addWidget(itens)

        return layout

    def _font_bold(self) -> QFont:
        font = QFont()
        font.setBold(True)
        return font

    def _dados_mockados(self) -> list[dict]:
        return self.invoice_data["rows"]

    def _exportar_dados_cartao(self) -> None:
        resposta = QMessageBox.question(
            self,
            "Exportar dados do cartão",
            "Deseja exportar em formato SQLite portátil?\n\n"
            "Sim = SQLite\n"
            "Não = Excel\n"
            "Cancelar = CSV",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )

        if resposta == QMessageBox.Yes:
            caminho, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar cartão em SQLite",
                "cartao_exportado.db",
                "Banco SQLite (*.db)",
            )

            if not caminho:
                return

            self.portable_data_service.exportar_db(
                credit_card=self.credit_card,
                destino=caminho,
            )

        elif resposta == QMessageBox.No:
            caminho, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar cartão em Excel",
                "cartao_exportado.xlsx",
                "Planilha Excel (*.xlsx)",
            )

            if not caminho:
                return

            self.portable_data_service.exportar_excel(
                credit_card=self.credit_card,
                destino=caminho,
            )

        else:
            caminho, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar cartão em CSV",
                "cartao_exportado.csv",
                "CSV (*.csv)",
            )

            if not caminho:
                return

            self.portable_data_service.exportar_csv(
                credit_card=self.credit_card,
                destino=caminho,
            )

        QMessageBox.information(
            self,
            "Exportação concluída",
            "Os dados deste cartão foram exportados com sucesso.",
        )

    def _importar_dados_cartao(self) -> None:
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Importar dados do cartão",
            "",
            "Arquivos suportados (*.db *.xlsx *.csv)",
        )

        if not caminho:
            return

        try:
            if caminho.lower().endswith(".db"):
                total = self.portable_data_service.importar_db(
                    credit_card=self.credit_card,
                    origem=caminho,
                    category_id=1,
                )

            elif caminho.lower().endswith(".xlsx"):
                total = self.portable_data_service.importar_excel(
                    credit_card=self.credit_card,
                    origem=caminho,
                    category_id=1,
                )

            elif caminho.lower().endswith(".csv"):
                total = self.portable_data_service.importar_csv(
                    credit_card=self.credit_card,
                    origem=caminho,
                    category_id=1,
                )

            else:
                QMessageBox.warning(
                    self,
                    "Formato inválido",
                    "Selecione um arquivo .db, .xlsx ou .csv.",
                )
                return

        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao importar dados",
                str(erro),
            )
            return

        self.invoice_data = self._carregar_fatura_selecionada()

        self._sincronizar_fatura_com_saldo()

        self._recarregar_tabela()
        self.data_changed.emit()

        QMessageBox.information(
            self,
            "Importação concluída",
            f"{total} lançamentos foram importados para este cartão.",
        )

    def _importar_csv(self) -> None:
        csv_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar CSV",
            "",
            "Arquivos CSV (*.csv)",
        )

        if not csv_path:
            return

        try:
            expenses = self.import_service.importar_preview(
                csv_path
            )
        except Exception as erro:
            QMessageBox.critical(
                self,
                "Erro ao importar CSV",
                f"Não foi possível importar o arquivo.\n\n{erro}",
            )
            return

        if not expenses:
            QMessageBox.information(
                self,
                "Importação",
                "Nenhuma compra importável foi encontrada no CSV.",
            )
            return

        dialog = CreditCardImportPreviewDialog(
            expenses=expenses,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        adjustments = self.import_service.csv_handler.import_adjustments(
            csv_path
        )

        pagamentos = [
            adjustment
            for adjustment in adjustments
            if adjustment.adjustment_type == "payment_received"
        ]

        pagamentos_fatura_anterior = set()

        if pagamentos:
            previous_payment_dialog = CreditCardPreviousPaymentDialog(
                adjustments=pagamentos,
                parent=self,
            )

            if previous_payment_dialog.exec() != QDialog.Accepted:
                return

            pagamentos_fatura_anterior = (
                previous_payment_dialog.obter_pagamentos_fatura_anterior()
            )

        total_salvo = self.import_service.confirmar_importacao(
            credit_card=self.credit_card,
            expenses=expenses,
            category_id=1,
        )

        total_ajustes = self.import_service.importar_ajustes_csv(
            credit_card=self.credit_card,
            csv_path=csv_path,
            previous_payment_keys=pagamentos_fatura_anterior,
        )

        QMessageBox.information(
            self,
            "Importação concluída",
            f"{total_salvo} lançamentos foram salvos no banco.\n"
            f"{total_ajustes} ajustes de fatura foram importados.",
        )

        self.invoice_data = self._carregar_fatura_selecionada()

        self._sincronizar_fatura_com_saldo()

        self._recarregar_tabela()
        self.data_changed.emit()

    def _sincronizar_fatura_com_saldo(self) -> None:
        try:
            self.balance_sync_service.sincronizar_fatura_com_saldo(
                credit_card_id=self.credit_card["id"],
                invoice_year=self.invoice_data["invoice_year"],
                invoice_month=self.invoice_data["invoice_month"],
            )

        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao sincronizar com Saldo",
                str(erro),
            )

    def _recarregar_tabela(self) -> None:
        nova_tabela = self._criar_tabela()

        parent_layout = self.content_layout

        parent_layout.replaceWidget(
            self.table,
            nova_tabela,
        )

        self.table.deleteLater()
        self.table = nova_tabela

        self._aplicar_filtros_tabela()

    def _reprocessar_faturas(self) -> None:
        total = self.detail_service.reprocessar_faturas_cartao(
            credit_card=self.credit_card,
        )

        self.invoice_data = self._carregar_fatura_selecionada()

        self._sincronizar_fatura_com_saldo()

        self._recarregar_tabela()

        self.data_changed.emit()

        QMessageBox.information(
            self,
            "Faturas reprocessadas",
            f"{total} lançamentos foram reprocessados.",
        )

    def _aplicar_filtros_tabela(self) -> None:
        texto_busca = ""

        if hasattr(self, "busca_input"):
            texto_busca = self.busca_input.text().strip().lower()

        categoria_id = None

        if hasattr(self, "categoria_filter_combo"):
            categoria_id = self.categoria_filter_combo.currentData()

        for row_index in range(self.table.rowCount()):
            item = self.table.item(row_index, 2)

            if item is None:
                self.table.setRowHidden(row_index, False)
                continue

            row_data = item.data(Qt.UserRole)

            if not row_data or row_data.get("type") != "expense":
                self.table.setRowHidden(row_index, False)
                continue

            mostrar = True

            if texto_busca:
                descricao = str(row_data.get("description", "")).lower()
                categoria = str(row_data.get("category", "")).lower()

                mostrar = (
                        texto_busca in descricao
                        or texto_busca in categoria
                )

            if categoria_id is not None:
                mostrar = (
                        mostrar
                        and row_data.get("category_id") == categoria_id
                )

            self.table.setRowHidden(row_index, not mostrar)

    def _alterar_categoria_lancamento(
            self,
            expense_id: int | None,
            category_id: int,
            row_index: int,
    ) -> None:
        if expense_id is None:
            QMessageBox.warning(
                self,
                "Categoria não alterada",
                "Este lançamento não possui ID no banco.",
            )
            return

        try:
            self.detail_service.atualizar_categoria_lancamento(
                expense_id=expense_id,
                category_id=category_id,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao alterar categoria",
                str(erro),
            )
            return

        categoria = next(
            (
                categoria
                for categoria in self.categories
                if categoria["id"] == category_id
            ),
            None,
        )

        if categoria:
            cor_item = self.table.item(row_index, 1)

            if cor_item:
                cor_item.setBackground(
                    QColor(categoria["color"])
                )

        self.invoice_data = self._carregar_fatura_selecionada()

        self._recarregar_tabela()

        self.data_changed.emit()

    def _abrir_dialog_novo_lancamento(self) -> None:
        dialog = CreditCardExpenseDialog(
            categories=self.categories,
            invoice_year=self.invoice_data["invoice_year"],
            row_data=row_data,
            mode="edit",
            parent=self,
        )

        exclusao_solicitada = {
            "valor": False
        }

        dialog.delete_requested.connect(
            lambda: exclusao_solicitada.update(
                valor=True
            )
        )

        resultado = dialog.exec()

        if exclusao_solicitada["valor"]:
            self._excluir_lancamento(
                row_data=row_data,
            )
            return

        if resultado != QDialog.Accepted:
            return

        dados_lancamento = dialog.obter_dados()

        try:
            self.detail_service.criar_lancamento_manual(
                credit_card=self.credit_card,
                **dados_lancamento,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao criar lançamento",
                str(erro),
            )
            return

        self.invoice_data = self._carregar_fatura_selecionada()

        self._sincronizar_fatura_com_saldo()

        self._recarregar_tabela()
        self.data_changed.emit()

    def _editar_lancamento_duplo_clique(
            self,
            row_index: int,
            column_index: int,
    ) -> None:
        item = self.table.item(row_index, 2)

        if item is None:
            return

        row_data = item.data(Qt.UserRole)

        if not row_data or row_data.get("type") != "expense":
            return

        self._abrir_dialog_edicao_lancamento(row_data)

    def _abrir_dialog_edicao_lancamento(
            self,
            row_data: dict,
    ) -> None:
        dialog = CreditCardExpenseDialog(
            categories=self.categories,
            invoice_year=self.invoice_data["invoice_year"],
            row_data=row_data,
            mode="edit",
            parent=self,
        )

        exclusao_solicitada = {
            "valor": False
        }

        dialog.delete_requested.connect(
            lambda: exclusao_solicitada.update(
                valor=True
            )
        )

        resultado = dialog.exec()

        # IMPORTANTE:
        # verificar exclusão ANTES de verificar Accepted/Rejected
        if exclusao_solicitada["valor"]:
            self._excluir_lancamento(
                row_data=row_data,
            )
            return

        if resultado != QDialog.Accepted:
            return

        dados_lancamento = dialog.obter_dados()

        dados_lancamento.pop(
            "installment_number",
            None,
        )

        dados_lancamento.pop(
            "installment_total",
            None,
        )

        try:
            self.detail_service.atualizar_lancamento(
                credit_card=self.credit_card,
                expense_id=row_data["expense_id"],
                **dados_lancamento,
            )

        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao editar lançamento",
                str(erro),
            )
            return

        self.invoice_data = (
            self._carregar_fatura_selecionada()
        )

        self._sincronizar_fatura_com_saldo()

        self._recarregar_tabela()

        self.data_changed.emit()

    def _abrir_dialog_vincular_conta(self) -> None:
        contas = self.balance_account_service.listar_contas()

        conta_selecionada = {}

        dialog = CreditCardAccountLinkDialog(
            accounts=contas,
            current_account_id=self.credit_card.get("account_id"),
            parent=self,
        )

        dialog.account_selected.connect(
            lambda account: conta_selecionada.update(account)
        )

        if dialog.exec() != QDialog.Accepted:
            return

        if not conta_selecionada:
            return

        try:
            self.account_link_service.vincular_cartao_a_conta(
                credit_card_id=self.credit_card["id"],
                account_id=conta_selecionada["id"],
                sincronizar_com_saldo=True,
                atualizar_compromissos_existentes=True,
            )

            self.credit_card["account_id"] = conta_selecionada["id"]
            self.credit_card["sync_with_balance"] = 1

            self._sincronizar_fatura_com_saldo()

        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao vincular conta",
                str(erro),
            )
            return

        QMessageBox.information(
            self,
            "Conta vinculada",
            f"O cartão foi vinculado à conta {conta_selecionada['name']}.",
        )

        self.data_changed.emit()

    def _excluir_lancamento(
            self,
            row_data: dict,
    ) -> None:
        expense_id = row_data.get("expense_id")

        if expense_id is None:
            QMessageBox.warning(
                self,
                "Não foi possível excluir",
                "Este lançamento não possui ID no banco.",
            )
            return

        try:
            analise = (
                self.detail_service.analisar_exclusao_lancamento(
                    credit_card=self.credit_card,
                    expense_id=expense_id,
                )
            )

        except Exception as erro:
            QMessageBox.warning(
                self,
                "Não foi possível excluir",
                str(erro),
            )
            return

        if analise["adiantada"]:
            QMessageBox.information(
                self,
                "Parcela adiantada",
                "Para apagar parcelas adiantadas, primeiro é necessário "
                "reajustar as parcelas extras dessa fatura para seu mês original.",
            )
            return

        if not analise["parcelado"]:
            self._confirmar_exclusao_lancamento_unico(
                expense_id=expense_id,
            )
            return

        self._escolher_exclusao_parcelamento(
            expense_id=expense_id,
            installment_number=analise["installment_number"],
            installment_total=analise["installment_total"],
        )

    def _confirmar_exclusao_lancamento_unico(
            self,
            expense_id: int,
    ) -> None:
        resposta = QMessageBox.question(
            self,
            "Excluir lançamento",
            "Deseja realmente excluir este lançamento?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        self._executar_exclusao_lancamento(
            expense_id=expense_id,
            modo="unico",
        )

    def _escolher_exclusao_parcelamento(
            self,
            expense_id: int,
            installment_number: int,
            installment_total: int,
    ) -> None:
        mensagem = QMessageBox(self)

        mensagem.setWindowTitle(
            "Excluir parcela"
        )

        mensagem.setIcon(
            QMessageBox.Question
        )

        mensagem.setText(
            f"Esta compra pertence a um parcelamento "
            f"({installment_number}/{installment_total})."
        )

        mensagem.setInformativeText(
            "Escolha o que deseja excluir."
        )

        botao_unico = mensagem.addButton(
            "Apenas esta parcela",
            QMessageBox.ActionRole,
        )

        botao_seguintes = mensagem.addButton(
            "Esta e as seguintes",
            QMessageBox.ActionRole,
        )

        botao_tudo = mensagem.addButton(
            "Todo o parcelamento",
            QMessageBox.DestructiveRole,
        )

        mensagem.addButton(
            "Cancelar",
            QMessageBox.RejectRole,
        )

        mensagem.exec()

        botao_clicado = mensagem.clickedButton()

        if botao_clicado == botao_unico:
            modo = "unico"

        elif botao_clicado == botao_seguintes:
            modo = "deste_em_diante"

        elif botao_clicado == botao_tudo:
            modo = "parcelamento_inteiro"

        else:
            return

        self._executar_exclusao_lancamento(
            expense_id=expense_id,
            modo=modo,
        )

    def _executar_exclusao_lancamento(
            self,
            expense_id: int,
            modo: str,
    ) -> None:
        try:
            self.detail_service.excluir_lancamento(
                credit_card=self.credit_card,
                expense_id=expense_id,
                modo=modo,
                reference_invoice_year=self.invoice_data["invoice_year"],
                reference_invoice_month=self.invoice_data["invoice_month"],
            )

        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao excluir lançamento",
                str(erro),
            )
            return

        self.invoice_data = (
            self._carregar_fatura_selecionada()
        )

        self._sincronizar_fatura_com_saldo()

        self._recarregar_tabela()

        self.data_changed.emit()

