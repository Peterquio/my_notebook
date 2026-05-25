from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.finance_category_service import (
    FinanceCategoryService,
)

from ui.dialogs.color_picker_dialog import (
    escolher_cor,
)

class FinanceCategoryManagerDialog(QDialog):
    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username
        self.service = FinanceCategoryService(username)

        self.setWindowTitle("Categorias de Gastos")
        self.resize(760, 560)
        self.setMinimumSize(680, 500)

        self.selected_color = "#7C3AED"

        self.category_rows = []

        self._aplicar_estilo()
        self._montar_interface()
        self._carregar_categorias()

    def _aplicar_estilo(self) -> None:
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

            QLineEdit, QSpinBox {
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
            """
        )

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(18)

        header = QVBoxLayout()
        header.setSpacing(4)

        titulo = QLabel("Categorias de Gastos")
        titulo.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo = QLabel(
            "Gerencie as categorias globais usadas em todos os cartões."
        )
        subtitulo.setStyleSheet(
            "font-size: 13px; color: #64748b;"
        )

        header.addWidget(titulo)
        header.addWidget(subtitulo)

        layout.addLayout(header)

        layout.addWidget(
            self._criar_formulario()
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.lista_container = QWidget()
        self.lista_layout = QVBoxLayout(self.lista_container)
        self.lista_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_layout.setSpacing(10)
        self.lista_layout.addStretch()

        self.scroll_area.setWidget(self.lista_container)

        layout.addWidget(self.scroll_area, 1)

        salvar_tudo = QPushButton("Salvar alterações")
        salvar_tudo.setCursor(Qt.PointingHandCursor)
        salvar_tudo.clicked.connect(self._salvar_todas_categorias)
        salvar_tudo.setStyleSheet(
            """
            QPushButton {
                background-color: #6d28d9;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 16px;
            }

            QPushButton:hover {
                background-color: #5b21b6;
            }
            """
        )

        fechar = QPushButton("Fechar")
        fechar.setCursor(Qt.PointingHandCursor)
        fechar.clicked.connect(self.close)
        fechar.setFixedWidth(120)

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(salvar_tudo)
        footer.addWidget(fechar)

        layout.addLayout(footer)

    def _criar_formulario(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            """
        )

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome da nova categoria")

        self.cor_preview = QLabel()
        self.cor_preview.setFixedSize(38, 38)
        self.cor_preview.setStyleSheet(
            f"""
            background-color: {self.selected_color};
            border-radius: 19px;
            border: 1px solid #e2e8f0;
            """
        )

        escolher_cor = QPushButton("Cor")
        escolher_cor.setCursor(Qt.PointingHandCursor)
        escolher_cor.clicked.connect(self._escolher_cor)

        criar = QPushButton("+ Criar categoria")
        criar.setCursor(Qt.PointingHandCursor)
        criar.clicked.connect(self._criar_categoria)
        criar.setStyleSheet(
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

        layout.addWidget(self.nome_input, 1)
        layout.addWidget(self.cor_preview)
        layout.addWidget(escolher_cor)
        layout.addWidget(criar)

        return frame

    def _carregar_categorias(self) -> None:
        self._limpar_lista()
        self.category_rows = []

        categorias = self.service.listar_categorias_ativas()

        for categoria in categorias:
            card = self._criar_card_categoria(categoria)
            self.lista_layout.insertWidget(
                self.lista_layout.count() - 1,
                card,
            )

    def _limpar_lista(self) -> None:
        while self.lista_layout.count() > 1:
            item = self.lista_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _criar_card_categoria(
            self,
            categoria: dict,
    ) -> QFrame:
        card = QFrame()
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
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        cor = categoria["color"]

        bolinha = QPushButton()
        bolinha.setCursor(Qt.PointingHandCursor)
        bolinha.setFixedSize(28, 28)
        bolinha.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {cor};
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }}

            QPushButton:hover {{
                border: 2px solid #0f172a;
            }}
            """
        )

        cor_editada = {
            "value": cor,
        }

        bolinha.clicked.connect(
            lambda checked=False,
                   botao=bolinha,
                   cor_estado=cor_editada: self._editar_cor_categoria(
                botao=botao,
                cor_estado=cor_estado,
            )
        )

        nome = QLineEdit(categoria["name"])

        ordem = QSpinBox()
        ordem.setMinimum(1)
        ordem.setMaximum(99)
        ordem.setValue(categoria["display_number"])
        ordem.setFixedWidth(80)

        remover = QPushButton("Remover")
        remover.setCursor(Qt.PointingHandCursor)
        remover.clicked.connect(
            lambda: self._remover_categoria(
                categoria["id"],
                categoria["name"],
            )
        )

        if categoria.get("is_protected"):
            nome.setEnabled(False)
            ordem.setEnabled(False)
            remover.setEnabled(False)
            remover.setText("Protegida")

        layout.addWidget(bolinha)
        layout.addWidget(nome, 1)
        layout.addWidget(QLabel("Ordem"))
        layout.addWidget(ordem)
        layout.addWidget(remover)

        self.category_rows.append(
            {
                "id": categoria["id"],
                "nome_input": nome,
                "ordem_input": ordem,
                "cor_estado": cor_editada,
                "is_protected": categoria.get("is_protected"),
            }
        )

        return card

    def _escolher_cor(self) -> None:
        cor = escolher_cor(
            parent=self,
            cor_inicial=self.selected_color,
        )

        if not cor:
            return

        self.selected_color = cor

        self.cor_preview.setStyleSheet(
            f"""
            background-color: {self.selected_color};
            border-radius: 19px;
            border: 1px solid #e2e8f0;
            """
        )

    def _criar_categoria(self) -> None:
        try:
            self.service.criar_categoria(
                name=self.nome_input.text(),
                color=self.selected_color,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Categoria inválida",
                str(erro),
            )
            return

        self.nome_input.clear()
        self._carregar_categorias()

    def _editar_cor_categoria(
            self,
            botao: QPushButton,
            cor_estado: dict,
    ) -> None:
        cor = escolher_cor(
            parent=self,
            cor_inicial=cor_estado["value"],
        )

        if not cor:
            return

        cor_estado["value"] = cor

        botao.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {cor};
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }}

            QPushButton:hover {{
                border: 2px solid #0f172a;
            }}
            """
        )

    def _salvar_todas_categorias(self) -> None:
        try:
            for row in self.category_rows:
                if row["is_protected"]:
                    continue

                self.service.atualizar_categoria(
                    category_id=row["id"],
                    name=row["nome_input"].text(),
                    color=row["cor_estado"]["value"],
                    display_number=row["ordem_input"].value(),
                )

        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao salvar categorias",
                str(erro),
            )
            return

        QMessageBox.information(
            self,
            "Categorias salvas",
            "As alterações foram salvas com sucesso.",
        )

        self._carregar_categorias()

    def _remover_categoria(
            self,
            category_id: int,
            name: str,
    ) -> None:
        resposta = QMessageBox.question(
            self,
            "Remover categoria",
            f"Deseja remover a categoria '{name}'?",
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.service.desativar_categoria(category_id)
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao remover categoria",
                str(erro),
            )
            return

        self._carregar_categorias()