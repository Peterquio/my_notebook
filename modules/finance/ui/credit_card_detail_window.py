from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
)


class CreditCardDetailWindow(QDialog):
    def __init__(
            self,
            credit_card: dict,
            parent=None,
    ) -> None:

        super().__init__(parent)

        self.credit_card = credit_card

        self.setWindowTitle(
            f"Cartão - {credit_card['name']}"
        )

        self.resize(1180, 760)
        self.setMinimumSize(1000, 650)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8fafc;
                color: #1e1b4b;
                font-family: Segoe UI;
            }

            QLabel {
                color: #1e1b4b;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 10px 14px;
                background-color: transparent;
                color: #475569;
                text-align: left;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
            }

            QLineEdit, QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 12px;
                background-color: white;
                color: #334155;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                gridline-color: #edf2f7;
                selection-background-color: #ede9fe;
                selection-color: #1e1b4b;
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

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self._criar_sidebar()
        self.content = self._criar_content()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content, 1)

    def _criar_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(160)
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
            font-size: 36px;
            font-weight: bold;
            color: #7c3aed;
            """
        )

        layout.addWidget(logo)
        layout.addSpacing(24)

        botoes = [
            ("Resumo", True),
            ("Lançamentos", False),
            ("Categorias", False),
            ("Cartão", False),
            ("Configurações", False),
            ("Ajuda", False),
        ]

        for texto, ativo in botoes:
            botao = QPushButton(texto)

            if ativo:
                botao.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #f3e8ff;
                        color: #7c3aed;
                        font-weight: bold;
                        border-radius: 10px;
                        text-align: left;
                    }
                    """
                )

            layout.addWidget(botao)

        layout.addStretch()

        sair = QPushButton("Sair")
        sair.clicked.connect(self.close)
        layout.addWidget(sair)

        return sidebar

    def _criar_content(self) -> QWidget:
        content = QWidget()

        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(22)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title_area = QVBoxLayout()
        title_area.setSpacing(4)

        title = QLabel(
            f"Cartão de Crédito {self.credit_card['name']}"
        )
        title.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            color: #1e1b4b;
            """
        )

        subtitle = QLabel(
            (
                f"Fechamento dia {self.credit_card['closing_day']} • "
                f"Vencimento dia {self.credit_card['due_day']}"
            )
        )
        subtitle.setStyleSheet(
            "font-size: 13px; color: #64748b;"
        )

        title_area.addWidget(title)
        title_area.addWidget(subtitle)

        header_layout.addLayout(title_area)
        header_layout.addStretch()

        vencimento_card = self._criar_info_card(
            titulo="Vencimento",
            valor=f"{self.credit_card['due_day']:02d}/04",
            largura=145,
        )

        total_card = self._criar_total_card()

        header_layout.addWidget(vencimento_card)
        header_layout.addWidget(total_card)

        layout.addLayout(header_layout)

        resumo_layout = QHBoxLayout()
        resumo_layout.setSpacing(18)

        resumo_layout.addWidget(
            self._criar_gastos_categoria_card()
        )
        resumo_layout.addWidget(
            self._criar_resumo_categoria_card()
        )
        resumo_layout.addWidget(
            self._criar_insight_card()
        )

        layout.addLayout(resumo_layout)

        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(12)

        busca = QLineEdit()
        busca.setPlaceholderText("Buscar lançamentos...")
        busca.setFixedWidth(230)

        filtro_todos = QPushButton("Todos")
        filtro_todos.setFixedWidth(80)
        filtro_todos.setStyleSheet(
            """
            QPushButton {
                background-color: #f3e8ff;
                color: #7c3aed;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
            }
            """
        )

        filtro_mes = QComboBox()
        filtro_mes.addItems(
            [
                "Este mês",
                "Próximo mês",
                "Mês anterior",
            ]
        )
        filtro_mes.setFixedWidth(130)

        filtro_extra = QPushButton("Mais filtros")
        filtro_extra.setFixedWidth(120)
        filtro_extra.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                text-align: center;
            }
            """
        )

        exportar = QPushButton("Exportar")
        exportar.setFixedWidth(105)
        exportar.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                text-align: center;
            }
            """
        )

        filtros_layout.addWidget(busca)
        filtros_layout.addWidget(filtro_todos)
        filtros_layout.addWidget(filtro_mes)
        filtros_layout.addWidget(filtro_extra)
        filtros_layout.addStretch()
        filtros_layout.addWidget(exportar)

        layout.addLayout(filtros_layout)

        self.table = self._criar_tabela_lancamentos()
        layout.addWidget(self.table, 1)

        footer_layout = QHBoxLayout()

        footer_text = QLabel(
            "Mostrando 1–26 de 26 lançamentos"
        )
        footer_text.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()

        page = QLabel("1")
        page.setAlignment(Qt.AlignCenter)
        page.setFixedSize(32, 32)
        page.setStyleSheet(
            """
            background-color: #7c3aed;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            """
        )

        footer_layout.addWidget(page)

        layout.addLayout(footer_layout)

        return content

    def _criar_info_card(
            self,
            titulo: str,
            valor: str,
            largura: int,
    ) -> QFrame:

        card = QFrame()
        card.setFixedWidth(largura)
        card.setFixedHeight(76)
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(
            "font-size: 11px; color: #64748b;"
        )

        label_valor = QLabel(valor)
        label_valor.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #1e1b4b;"
        )

        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)

        return card

    def _criar_total_card(self) -> QFrame:
        card = QFrame()
        card.setFixedWidth(250)
        card.setFixedHeight(96)
        card.setStyleSheet(
            """
            QFrame {
                background-color: #7c3aed;
                border-radius: 14px;
            }

            QLabel {
                color: white;
            }
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        titulo = QLabel("Total Fatura")
        titulo.setStyleSheet(
            "font-size: 12px; color: #ede9fe;"
        )

        valor = QLabel("R$ 5.054,52")
        valor.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: white;"
        )

        layout.addWidget(titulo)
        layout.addWidget(valor)

        return card

    def _criar_gastos_categoria_card(self) -> QFrame:
        card = self._card_base()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        titulo = QLabel("Gastos por categoria")
        titulo.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        categorias = [
            ("Casa", "R$ 806,87", "#ef4444", 0.22),
            ("Assinaturas", "R$ 267,50", "#3b82f6", 0.14),
            ("Outros", "R$ 3.980,15", "#7c3aed", 0.78),
        ]

        for nome, valor, cor, largura in categorias:
            linha = QVBoxLayout()

            topo = QHBoxLayout()
            label = QLabel(f"● {nome}")
            label.setStyleSheet(
                f"font-size: 12px; color: {cor};"
            )

            value = QLabel(valor)
            value.setAlignment(Qt.AlignRight)
            value.setStyleSheet(
                "font-size: 12px; color: #334155;"
            )

            topo.addWidget(label)
            topo.addStretch()
            topo.addWidget(value)

            barra_fundo = QFrame()
            barra_fundo.setFixedHeight(5)
            barra_fundo.setStyleSheet(
                """
                background-color: #e5e7eb;
                border-radius: 3px;
                """
            )

            barra = QFrame(barra_fundo)
            barra.setGeometry(
                0,
                0,
                int(230 * largura),
                5,
            )
            barra.setStyleSheet(
                f"""
                background-color: {cor};
                border-radius: 3px;
                """
            )

            linha.addLayout(topo)
            linha.addWidget(barra_fundo)

            layout.addLayout(linha)

        layout.addStretch()

        total = QHBoxLayout()

        total_label = QLabel("Total")
        total_label.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        total_valor = QLabel("R$ 5.054,52")
        total_valor.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #7c3aed;"
        )

        total.addWidget(total_label)
        total.addStretch()
        total.addWidget(total_valor)

        layout.addLayout(total)

        return card

    def _criar_resumo_categoria_card(self) -> QFrame:
        card = self._card_base()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        titulo = QLabel("Resumo por categoria")
        titulo.setStyleSheet(
            "font-size: 13px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        categorias = [
            ("Casa", "3 lançamentos", "R$ 806,87", "#ef4444"),
            ("Assinaturas", "7 lançamentos", "R$ 267,50", "#3b82f6"),
            ("Outros", "16 lançamentos", "R$ 3.980,15", "#7c3aed"),
        ]

        for nome, qtd, valor, cor in categorias:
            linha = QHBoxLayout()

            icone = QLabel("■")
            icone.setStyleSheet(
                f"font-size: 18px; color: {cor};"
            )
            icone.setFixedWidth(26)

            textos = QVBoxLayout()
            nome_label = QLabel(nome)
            nome_label.setStyleSheet(
                "font-size: 12px; font-weight: bold;"
            )

            qtd_label = QLabel(qtd)
            qtd_label.setStyleSheet(
                "font-size: 11px; color: #64748b;"
            )

            textos.addWidget(nome_label)
            textos.addWidget(qtd_label)

            valor_label = QLabel(valor)
            valor_label.setStyleSheet(
                "font-size: 12px; color: #334155;"
            )

            linha.addWidget(icone)
            linha.addLayout(textos)
            linha.addStretch()
            linha.addWidget(valor_label)

            layout.addLayout(linha)

        layout.addStretch()

        return card

    def _criar_insight_card(self) -> QFrame:
        card = self._card_base()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        icon = QLabel("%")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(48, 48)
        icon.setStyleSheet(
            """
            background-color: #f3e8ff;
            color: #7c3aed;
            border-radius: 12px;
            font-size: 24px;
            font-weight: bold;
            """
        )

        titulo = QLabel("Organize seus gastos")
        titulo.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        texto = QLabel(
            "Veja seus gastos por categoria e tenha mais controle financeiro."
        )
        texto.setWordWrap(True)
        texto.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        botao = QPushButton("Ver insights  →")
        botao.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                color: #1e1b4b;
                text-align: center;
            }
            """
        )

        layout.addWidget(icon)
        layout.addWidget(titulo)
        layout.addWidget(texto)
        layout.addStretch()
        layout.addWidget(botao)

        return card

    def _card_base(self) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(210)
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            """
        )

        return card

    def _criar_tabela_lancamentos(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(
            [
                "DATA",
                "LANÇAMENTO",
                "CATEGORIA",
                "PARCELAS",
                "VALOR ORIGINAL",
                "VALOR NA FATURA",
            ]
        )

        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        table.setColumnWidth(0, 90)
        table.setColumnWidth(2, 150)
        table.setColumnWidth(3, 90)
        table.setColumnWidth(4, 140)
        table.setColumnWidth(5, 140)

        rows = self._dados_mockados()

        table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            if row["type"] == "group":
                self._adicionar_linha_grupo(
                    table,
                    row_index,
                    row,
                )
            else:
                self._adicionar_linha_lancamento(
                    table,
                    row_index,
                    row,
                )

        table.setRowHeight(table.rowCount() - 1, 44)

        return table

    def _adicionar_linha_grupo(
            self,
            table: QTableWidget,
            row_index: int,
            row: dict,
    ) -> None:

        cor = row["color"]

        for col in range(table.columnCount()):
            item = QTableWidgetItem("")
            item.setBackground(
                QColor(row["background"])
            )
            table.setItem(row_index, col, item)

        item_nome = QTableWidgetItem(
            f"■  {row['name']}"
        )
        item_nome.setForeground(
            QColor(cor)
        )
        item_nome.setBackground(
            QColor(row["background"])
        )
        item_nome.setFlags(Qt.ItemIsEnabled)
        table.setItem(row_index, 1, item_nome)

        item_qtd = QTableWidgetItem(
            row["count"]
        )
        item_qtd.setTextAlignment(Qt.AlignCenter)
        item_qtd.setForeground(QColor("#475569"))
        item_qtd.setBackground(QColor(row["background"]))
        table.setItem(row_index, 4, item_qtd)

        item_total = QTableWidgetItem(
            row["total"]
        )
        item_total.setTextAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )
        item_total.setForeground(
            QColor(cor)
        )
        item_total.setBackground(
            QColor(row["background"])
        )
        table.setItem(row_index, 5, item_total)

        table.setRowHeight(row_index, 38)

    def _adicionar_linha_lancamento(
            self,
            table: QTableWidget,
            row_index: int,
            row: dict,
    ) -> None:

        valores = [
            row["date"],
            row["description"],
            row["category"],
            row["installment"],
            row["remaining"],
            row["amount"],
        ]

        for col, value in enumerate(valores):
            item = QTableWidgetItem(value)

            if col in [3, 4, 5]:
                item.setTextAlignment(
                    Qt.AlignRight | Qt.AlignVCenter
                )
            else:
                item.setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                )

            item.setForeground(
                QColor("#334155")
            )

            table.setItem(row_index, col, item)

        table.setRowHeight(row_index, 34)

    def _dados_mockados(self) -> list[dict]:
        return [
            {
                "type": "group",
                "name": "Casa",
                "count": "3 lançamentos",
                "total": "R$ 806,87",
                "color": "#ef4444",
                "background": "#fef2f2",
            },
            {
                "type": "expense",
                "date": "02/06",
                "description": "Luz",
                "category": "Casa",
                "installment": "01/01",
                "remaining": "R$ 593,44",
                "amount": "R$ 593,44",
            },
            {
                "type": "expense",
                "date": "08/06",
                "description": "Internet",
                "category": "Casa",
                "installment": "01/01",
                "remaining": "R$ 213,43",
                "amount": "R$ 213,43",
            },
            {
                "type": "group",
                "name": "Assinaturas",
                "count": "7 lançamentos",
                "total": "R$ 267,50",
                "color": "#3b82f6",
                "background": "#eff6ff",
            },
            {
                "type": "expense",
                "date": "05/06",
                "description": "Amazon Prime",
                "category": "Assinatura",
                "installment": "01/01",
                "remaining": "-",
                "amount": "R$ 13,90",
            },
            {
                "type": "expense",
                "date": "17/06",
                "description": "Spotify",
                "category": "Assinatura",
                "installment": "01/01",
                "remaining": "-",
                "amount": "R$ 23,90",
            },
            {
                "type": "group",
                "name": "Outros",
                "count": "16 lançamentos",
                "total": "R$ 3.980,15",
                "color": "#7c3aed",
                "background": "#faf5ff",
            },
            {
                "type": "expense",
                "date": "08/06",
                "description": "Celular POCO X6 PRO",
                "category": "Compras",
                "installment": "10/10",
                "remaining": "R$ 191,54",
                "amount": "R$ 191,54",
            },
            {
                "type": "expense",
                "date": "06/07",
                "description": "Pokemon TCG Mini Tin Eevee",
                "category": "Lazer",
                "installment": "09/12",
                "remaining": "R$ 539,96",
                "amount": "R$ 134,99",
            },
            {
                "type": "expense",
                "date": "11/12",
                "description": "Colete Social - ML",
                "category": "Compras",
                "installment": "04/06",
                "remaining": "R$ 66,45",
                "amount": "R$ 22,15",
            },
            {
                "type": "expense",
                "date": "06/01",
                "description": "CD Taylor - Kiwi - Universal",
                "category": "Entretenimento",
                "installment": "03/10",
                "remaining": "R$ 91,12",
                "amount": "R$ 11,39",
            },
            {
                "type": "expense",
                "date": "16/01",
                "description": "DBD - PSN",
                "category": "Jogos",
                "installment": "03/04",
                "remaining": "R$ 11,10",
                "amount": "R$ 5,55",
            },
            {
                "type": "expense",
                "date": "25/02",
                "description": "Cama Box Queen Size",
                "category": "Casa",
                "installment": "02/10",
                "remaining": "R$ 2.292,12",
                "amount": "R$ 254,68",
            },
            {
                "type": "expense",
                "date": "13/03",
                "description": "Aliança de Noivado - Maridinho",
                "category": "Presentes",
                "installment": "01/10",
                "remaining": "R$ 2.472,00",
                "amount": "R$ 247,20",
            },
            {
                "type": "expense",
                "date": "20/03",
                "description": "10 Ideias de Dates - Hot Market",
                "category": "Entretenimento",
                "installment": "01/08",
                "remaining": "R$ 66,24",
                "amount": "R$ 8,28",
            },
        ]