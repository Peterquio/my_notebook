from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
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

from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)

from modules.finance.repositories.credit_card_invoice_repository import (
    CreditCardInvoiceRepository,
)

from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)

class CreditCardDetailWindow(QWidget):
    back_requested = Signal()
    data_changed = Signal()
    def __init__(
            self,
            credit_card: dict,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.credit_card = credit_card
        self.username = username
        self.import_service = CreditCardImportService(
            self.username
        )

        self.detail_service = CreditCardDetailService(
            username=self.username
        )

        self.invoice_data = self.detail_service.carregar_fatura_atual(
            self.credit_card
        )

        #self.setWindowTitle(
        #    f"Cartão - {credit_card['name']}"
        #)
        #self.resize(1280, 760)
        #self.setMinimumSize(1100, 680)

        self._aplicar_estilo_base()
        self._montar_interface()

    def _aplicar_estilo_base(self) -> None:
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8fafc;
                font-family: Segoe UI;
                color: #0f172a;
            }

            QLabel {
                color: #0f172a;
            }

            QLineEdit, QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 12px;
                color: #334155;
                font-size: 12px;
            }

            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 14px;
                color: #334155;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                gridline-color: #eef2f7;
                selection-background-color: #ede9fe;
                selection-color: #1e1b4b;
                font-size: 12px;
            }

            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-size: 11px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding: 10px;
            }
            """
        )

    def _montar_interface(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(
            self._criar_sidebar()
        )

        main_layout.addWidget(
            self._criar_area_principal(),
            1,
        )

    def _criar_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(150)
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-right: 1px solid #e2e8f0;
            }
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(10)

        logo = QLabel("nu")
        logo.setStyleSheet(
            """
            color: #7c3aed;
            font-size: 34px;
            font-weight: bold;
            """
        )

        layout.addWidget(logo)
        layout.addSpacing(28)

        botoes = [
            ("Dashboard", True),
            ("Categorias", False),
            ("Configurações", False),
        ]

        for texto, ativo in botoes:
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)

            if ativo:
                botao.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #f3e8ff;
                        color: #6d28d9;
                        border: none;
                        border-radius: 10px;
                        font-weight: bold;
                        text-align: left;
                        padding: 10px 12px;
                    }
                    """
                )
            else:
                botao.setStyleSheet(
                    """
                    QPushButton {
                        background-color: white;
                        color: #475569;
                        border: none;
                        border-radius: 10px;
                        text-align: left;
                        padding: 10px 12px;
                    }

                    QPushButton:hover {
                        background-color: #f8fafc;
                    }
                    """
                )

            layout.addWidget(botao)
        layout.addSpacing(18)

        meses_titulo = QLabel("Faturas")
        meses_titulo.setStyleSheet(
            """
            color: #64748b;
            font-size: 11px;
            font-weight: bold;
            """
        )
        layout.addWidget(meses_titulo)

        meses_visiveis = [
            "Fev/2026",
            "Mar/2026",
            "Abr/2026",
            "Mai/2026",
            "Jun/2026",
            "Jul/2026",
        ]

        for mes in meses_visiveis:
            botao_mes = QPushButton(mes)
            botao_mes.setCursor(Qt.PointingHandCursor)

            if mes == "Abr/2026":
                botao_mes.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #ede9fe;
                        color: #6d28d9;
                        border: none;
                        border-radius: 10px;
                        font-weight: bold;
                        text-align: left;
                        padding: 9px 12px;
                    }
                    """
                )
            else:
                botao_mes.setStyleSheet(
                    """
                    QPushButton {
                        background-color: white;
                        color: #64748b;
                        border: none;
                        border-radius: 10px;
                        text-align: left;
                        padding: 9px 12px;
                    }

                    QPushButton:hover {
                        background-color: #f8fafc;
                    }
                    """
                )

            layout.addWidget(botao_mes)

        layout.addStretch()

        sair = QPushButton("Sair")
        sair.clicked.connect(self.close)
        sair.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: #475569;
                border: none;
                text-align: left;
                padding: 10px 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
            }
            """
        )

        layout.addWidget(sair)

        return sidebar

    def _criar_area_principal(self) -> QWidget:
        area = QWidget()

        self.content_layout = QVBoxLayout(area)
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

        layout.addLayout(
            self._criar_footer()
        )

        return area

    def _criar_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        voltar = QPushButton("←")
        voltar.setFixedSize(38, 38)
        voltar.clicked.connect(
            self.back_requested.emit
        )

        layout.addWidget(voltar)

        reprocessar = QPushButton("↻ Reprocessar")
        reprocessar.clicked.connect(
            self._reprocessar_faturas
        )

        layout.addWidget(reprocessar)

        titulo = QLabel(
            f"Cartão de Crédito {self.credit_card['name']}"
        )
        titulo.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        selo = QLabel("Platinum")
        selo.setAlignment(Qt.AlignCenter)
        selo.setFixedSize(64, 24)
        selo.setStyleSheet(
            """
            background-color: #f3e8ff;
            color: #6d28d9;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            """
        )

        atualizado = QLabel(
            "Atualizado em 08/06/2026 às 09:30  ↻"
        )
        atualizado.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        layout.addWidget(titulo)
        layout.addWidget(selo)
        layout.addStretch()
        layout.addWidget(atualizado)

        return layout

    def _criar_cards_resumo(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(14)

        total_fatura = self.detail_service._formatar_moeda(
            self.invoice_data["total_fatura_cents"]
        )

        total_lancamentos = str(
            self.invoice_data["total_lancamentos"]
        )

        cards = [
            ("📅", "Vencimento", "10/04", "Faltam 2 dias"),
            ("💳", "Fatura Atual", total_fatura, "Total da fatura"),
            ("👛", "Limite Disponível", "R$ 6.945,48", "de R$ 12.000,00"),
            ("🕘", "Total Parcelado Futuro", "R$ 2.184,22", "Próximas parcelas"),
            ("🧾", "Total de Lançamentos", total_lancamentos, "Este mês"),
        ]

        for icon, title, value, subtitle in cards:
            layout.addWidget(
                self._criar_card_resumo(
                    icon,
                    title,
                    value,
                    subtitle,
                ),
                1,
            )

        return layout

    def _recarregar_resumo(self) -> None:
        self.invoice_data = self.detail_service.carregar_fatura_atual(
            self.credit_card
        )

        nova_area = self._criar_area_principal()

        layout_principal = self.layout()

        antigo_content = layout_principal.itemAt(1).widget()

        layout_principal.replaceWidget(
            antigo_content,
            nova_area,
        )

        antigo_content.deleteLater()

    def _criar_card_resumo(
            self,
            icon: str,
            title: str,
            value: str,
            subtitle: str,
    ) -> QFrame:
        card = QFrame()
        card.setFixedHeight(86)
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
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(42, 42)
        icon_label.setStyleSheet(
            """
            background-color: #f3e8ff;
            color: #6d28d9;
            border-radius: 21px;
            font-size: 20px;
            """
        )

        textos = QVBoxLayout()
        textos.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        value_label = QLabel(value)
        value_label.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "font-size: 11px; color: #64748b;"
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
        layout.setSpacing(10)

        busca = QLineEdit()
        busca.setPlaceholderText("Buscar lançamentos...")
        busca.setFixedWidth(230)

        categorias = QComboBox()
        categorias.addItems(
            [
                "Todas as categorias",
                "Gastos Fixos",
                "Assinatura",
                "Lazer",
                "Compras",
            ]
        )
        categorias.setFixedWidth(160)

        tipos = QComboBox()
        tipos.addItems(
            [
                "Todos",
                "Somente parcelados",
                "Somente à vista",
            ]
        )
        tipos.setFixedWidth(150)

        importar = QPushButton("Importar")
        importar.setFixedWidth(120)

        importar.clicked.connect(
            self._importar_csv
        )

        exportar = QPushButton("⬇  Exportar")
        exportar.setFixedWidth(105)

        novo = QPushButton("+  Novo lançamento")
        novo.setFixedWidth(150)
        novo.setStyleSheet(
            """
            QPushButton {
                background-color: #6d28d9;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 14px;
            }

            QPushButton:hover {
                background-color: #5b21b6;
            }
            """
        )

        layout.addWidget(busca)
        layout.addWidget(categorias)
        layout.addWidget(tipos)
        layout.addStretch()
        layout.addWidget(importar)
        layout.addWidget(exportar)
        layout.addWidget(novo)

        return layout

    def _criar_tabela(self) -> QTableWidget:
        table = QTableWidget()
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
        table.setAlternatingRowColors(False)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 26)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 170)
        table.setColumnWidth(5, 150)
        table.setColumnWidth(6, 150)

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

        for col, value in enumerate(valores):
            item = QTableWidgetItem(value)
            item.setForeground(QColor("#334155"))

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

        itens = QLabel("Itens por página:  50")
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

        total_salvo = self.import_service.confirmar_importacao(
            credit_card=self.credit_card,
            expenses=expenses,
            category_id=1,
        )

        QMessageBox.information(
            self,
            "Importação concluída",
            f"{total_salvo} lançamentos foram salvos no banco.",
        )

        self.invoice_data = self.detail_service.carregar_fatura_atual(
            self.credit_card
        )

        self._recarregar_resumo()
        self.data_changed.emit()

    def _recarregar_tabela(self) -> None:
        nova_tabela = self._criar_tabela()

        parent_layout = self.content_layout

        parent_layout.replaceWidget(
            self.table,
            nova_tabela,
        )

        self.table.deleteLater()
        self.table = nova_tabela

    def _reprocessar_faturas(self) -> None:
        expense_repository = CreditCardExpenseRepository(
            self.username
        )

        invoice_repository = CreditCardInvoiceRepository(
            self.username
        )

        invoice_service = CreditCardInvoiceService()

        total = invoice_service.reprocessar_faturas_cartao(
            credit_card=self.credit_card,
            expense_repository=expense_repository,
            invoice_repository=invoice_repository,
        )

        self.invoice_data = self.detail_service.carregar_fatura_atual(
            self.credit_card
        )

        self._recarregar_resumo()

        self.data_changed.emit()

        QMessageBox.information(
            self,
            "Faturas reprocessadas",
            f"{total} lançamentos foram reprocessados.",
        )