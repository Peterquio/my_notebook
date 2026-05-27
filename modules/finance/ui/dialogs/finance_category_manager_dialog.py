from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
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
        self.mostrar_inativas = False

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

            QLineEdit {
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
        self.lista_layout.setSpacing(4)
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

        categorias = self.service.listar_todas_categorias()

        categorias_ativas = [
            categoria
            for categoria in categorias
            if categoria["is_active"]
        ]

        categorias_inativas = [
            categoria
            for categoria in categorias
            if not categoria["is_active"]
        ]

        for categoria in categorias_ativas:
            card = self._criar_card_categoria(categoria)

            self.lista_layout.insertWidget(
                self.lista_layout.count() - 1,
                card,
            )

        if categorias_inativas:
            self._adicionar_bloco_inativas(
                categorias_inativas
            )

    def _adicionar_bloco_inativas(
            self,
            categorias_inativas: list[dict],
    ) -> None:
        botao = QPushButton(
            "▸ Categorias inativas"
            if not self.mostrar_inativas
            else "▾ Categorias inativas"
        )
        botao.setCursor(Qt.PointingHandCursor)
        botao.clicked.connect(
            self._alternar_bloco_inativas
        )
        botao.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #64748b;
                border: none;
                border-radius: 8px;
                text-align: left;
                font-size: 12px;
                font-weight: bold;
                padding: 8px 4px;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
                color: #334155;
            }
            """
        )

        self.lista_layout.insertWidget(
            self.lista_layout.count() - 1,
            botao,
        )

        if not self.mostrar_inativas:
            return

        for categoria in categorias_inativas:
            card = self._criar_card_categoria(categoria)

            self.lista_layout.insertWidget(
                self.lista_layout.count() - 1,
                card,
            )

    def _alternar_bloco_inativas(self) -> None:
        self.mostrar_inativas = not self.mostrar_inativas
        self._carregar_categorias()

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
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        cor = categoria["color"]

        bolinha = QPushButton()
        bolinha.setCursor(Qt.PointingHandCursor)
        bolinha.setFixedSize(22, 22)
        bolinha.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {cor};
                border-radius: 11px;
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
        nome.setFixedHeight(34)

        ordem = QLabel(str(categoria["display_number"] or 0))
        ordem.setAlignment(Qt.AlignCenter)
        ordem.setFixedSize(42, 34)
        ordem.setStyleSheet(
            """
            QLabel {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                color: #334155;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )

        subir = QPushButton("↑")
        subir.setFixedSize(34, 34)
        subir.setCursor(Qt.PointingHandCursor)

        descer = QPushButton("↓")
        descer.setFixedSize(34, 34)
        descer.setCursor(Qt.PointingHandCursor)

        remover = QPushButton("Remover")
        remover.setFixedHeight(34)
        remover.setCursor(Qt.PointingHandCursor)

        if categoria["is_active"]:
            subir.clicked.connect(
                lambda checked=False,
                       category_id=categoria["id"]: self._mover_categoria(
                    category_id=category_id,
                    direcao=-1,
                )
            )

            descer.clicked.connect(
                lambda checked=False,
                       category_id=categoria["id"]: self._mover_categoria(
                    category_id=category_id,
                    direcao=1,
                )
            )
            remover.setText("Remover")
            remover.clicked.connect(
                lambda: self._remover_categoria(
                    categoria["id"],
                    categoria["name"],
                )
            )
        else:
            remover.setText("Reativar")
            nome.setEnabled(False)
            ordem.setEnabled(False)
            subir.setEnabled(False)
            descer.setEnabled(False)
            bolinha.setEnabled(False)
            remover.clicked.connect(
                lambda: self._reativar_categoria(
                    categoria["id"],
                )
            )

            bolinha.setStyleSheet(
                """
                QPushButton {
                    background-color: #334155;
                    border-radius: 14px;
                    border: 1px solid #e2e8f0;
                }

                QPushButton:hover {
                    border: 2px solid #0f172a;
                }
                """
            )

        if categoria.get("is_protected"):
            nome.setEnabled(False)
            ordem.setEnabled(False)
            subir.setEnabled(False)
            descer.setEnabled(False)
            remover.setEnabled(False)
            remover.setText("Protegida")

        layout.addWidget(bolinha)
        layout.addWidget(nome, 1)
        layout.addWidget(QLabel("Ordem"))
        layout.addWidget(subir)
        layout.addWidget(ordem)
        layout.addWidget(descer)
        layout.addWidget(remover)

        self.category_rows.append(
            {
                "id": categoria["id"],
                "card": card,
                "nome_input": nome,
                "ordem_label": ordem,
                "display_number": categoria["display_number"] or 0,
                "is_active": categoria["is_active"],
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

    def _mover_categoria(
            self,
            category_id: int,
            direcao: int,
    ) -> None:
        linhas_ativas = [
            row
            for row in self.category_rows
            if row.get("is_active") and not row.get("is_protected")
        ]

        linhas_ativas.sort(
            key=lambda row: row["display_number"]
        )

        indice_atual = next(
            (
                index
                for index, row in enumerate(linhas_ativas)
                if row["id"] == category_id
            ),
            None,
        )

        if indice_atual is None:
            return

        novo_indice = indice_atual + direcao

        if novo_indice < 0 or novo_indice >= len(linhas_ativas):
            return

        linha_atual = linhas_ativas[indice_atual]
        linha_destino = linhas_ativas[novo_indice]

        linha_atual["display_number"], linha_destino["display_number"] = (
            linha_destino["display_number"],
            linha_atual["display_number"],
        )

        linha_atual["ordem_label"].setText(
            str(linha_atual["display_number"])
        )

        linha_destino["ordem_label"].setText(
            str(linha_destino["display_number"])
        )

        self._reordenar_cards_visualmente()

    def _reordenar_cards_visualmente(self) -> None:
        rows_ativas = [
            row
            for row in self.category_rows
            if row.get("is_active")
        ]

        rows_ativas.sort(
            key=lambda row: row["display_number"]
        )

        for row in rows_ativas:
            self.lista_layout.removeWidget(
                row["card"]
            )

        for index, row in enumerate(rows_ativas):
            self.lista_layout.insertWidget(
                index,
                row["card"]
            )

    def _salvar_todas_categorias(self) -> None:
        try:
            numeros_usados = {}

            for row in self.category_rows:
                if row["is_protected"]:
                    continue

                numero = row["display_number"]

                if numero in numeros_usados:
                    QMessageBox.warning(
                        self,
                        "Ordem duplicada",
                        f"O número {numero} foi usado em mais de uma categoria.",
                    )
                    return

                numeros_usados[numero] = row["id"]

            for row in self.category_rows:
                if row["is_protected"]:
                    continue

                self.service.atualizar_categoria(
                    category_id=row["id"],
                    name=row["nome_input"].text(),
                    color=row["cor_estado"]["value"],
                    display_number=row["display_number"],
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

    def _reativar_categoria(
            self,
            category_id: int,
    ) -> None:
        self.service.reativar_categoria(category_id)
        self._carregar_categorias()