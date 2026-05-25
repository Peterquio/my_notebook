from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


CORES_PADRAO = [
    "#660000", "#CC0000", "#FF3333", "#FF9999",
    "#FFCCE5", "#FF66B2", "#FF007F", "#99004C",
    "#994C00", "#FF8000", "#FFB266", "#FFE5CC",
    "#FFCCFF", "#FF66FF", "#990099", "#660066",
    "#666600", "#CCCC00", "#FFFF33", "#FFFFCC",
    "#CC99FF", "#9933FF", "#4C0099", "#190033",
    "#336600", "#66CC00", "#B2FF66", "#E5FFCC",
    "#9999FF", "#3333FF", "#0000CC", "#000066",
    "#003300", "#00CC00", "#66FF66", "#99FF99",
    "#66B2FF", "#0080FF", "#0066CC", "#003366",
    "#00994C", "#00FF80", "#99FFCC", "#CCFFE5",
    "#CCFFFF", "#66FFFF", "#009999", "#003333",
]


class HueBar(QWidget):
    hue_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setFixedWidth(28)
        self.setMinimumHeight(260)
        self.hue = 270

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        gradient = QLinearGradient(0, 0, 0, self.height())

        for i in range(0, 361, 30):
            color = QColor.fromHsv(i, 255, 255)
            gradient.setColorAt(i / 360, color)

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(
            self.rect(),
            12,
            12,
        )

        y = int((self.hue / 360) * self.height())
        y = max(8, min(y, self.height() - 8))

        painter.setPen(Qt.white)
        painter.drawEllipse(
            4,
            y - 6,
            20,
            12,
        )

    def mousePressEvent(self, event) -> None:
        self._atualizar_hue(event.position().y())

    def mouseMoveEvent(self, event) -> None:
        self._atualizar_hue(event.position().y())

    def _atualizar_hue(self, y: float) -> None:
        y = max(0, min(y, self.height() - 1))
        self.hue = int((y / max(1, self.height() - 1)) * 359)

        self.hue_changed.emit(self.hue)
        self.update()

class SaturationBar(QWidget):
    saturation_changed = Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setFixedWidth(28)
        self.setMinimumHeight(260)

        self.hue = 270
        self.saturation = 180

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            0,
            self.height(),
        )

        for i in range(0, 256, 20):
            color = QColor.fromHsv(
                self.hue,
                i,
                220,
            )

            gradient.setColorAt(
                i / 255,
                color,
            )

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)

        painter.drawRoundedRect(
            self.rect(),
            12,
            12,
        )

        y = int(
            (self.saturation / 255)
            * self.height()
        )
        y = max(8, min(y, self.height() - 8))

        painter.setPen(Qt.white)

        painter.drawEllipse(
            4,
            y - 6,
            20,
            12,
        )

    def mousePressEvent(self, event) -> None:
        self._atualizar_saturation(
            event.position().y()
        )

    def mouseMoveEvent(self, event) -> None:
        self._atualizar_saturation(
            event.position().y()
        )

    def _atualizar_saturation(
            self,
            y: float,
    ) -> None:
        y = max(
            0,
            min(y, self.height() - 1),
        )

        self.saturation = int(
            (y / max(1, self.height() - 1)) * 255
        )

        self.saturation_changed.emit(
            self.saturation
        )

        self.update()

class ColorPreview(QLabel):
    def __init__(self, color: str, parent=None) -> None:
        super().__init__(parent)

        self.setFixedSize(72, 72)
        self.set_color(color)

    def set_color(self, color: str) -> None:
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {color};
                border-radius: 36px;
                border: 3px solid white;
            }}
            """
        )


class ColorPickerDialog(QDialog):
    def __init__(
            self,
            cor_inicial: str = "#7C3AED",
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.resultado = None
        self.cor_atual = cor_inicial or "#7C3AED"
        qcolor = QColor(self.cor_atual)

        self.hue = qcolor.hue() if qcolor.hue() >= 0 else 270
        self.saturation = qcolor.saturation()
        self.value = qcolor.value()

        self.setWindowTitle("Escolher cor")
        self.setFixedSize(700, 520)

        self._aplicar_estilo()
        self._montar_interface()
        self._selecionar_cor(self.cor_atual)

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
                font-size: 13px;
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
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(16)

        titulo = QLabel("Escolher cor")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        subtitulo = QLabel(
            "Selecione uma cor da paleta ou ajuste pelo seletor Hue."
        )
        subtitulo.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        corpo = QHBoxLayout()
        corpo.setSpacing(18)

        painel = QFrame()
        painel.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
            }
            """
        )

        painel_layout = QVBoxLayout(painel)
        painel_layout.setContentsMargins(16, 16, 16, 16)
        painel_layout.setSpacing(14)

        topo = QHBoxLayout()

        self.preview = ColorPreview(self.cor_atual)

        textos = QVBoxLayout()
        textos.setSpacing(6)

        self.hex_input = QLineEdit()
        self.hex_input.setText(self.cor_atual)
        self.hex_input.editingFinished.connect(
            self._aplicar_hex_digitado
        )
        self.hex_input.returnPressed.connect(
            self._aplicar_hex_digitado
        )

        hex_label = QLabel("Código HEX")
        hex_label.setStyleSheet(
            "font-size: 12px; color: #64748b; font-weight: bold;"
        )

        hex_layout = QHBoxLayout()

        aplicar_hex = QPushButton("Aplicar")
        aplicar_hex.setCursor(Qt.PointingHandCursor)
        aplicar_hex.clicked.connect(
            self._aplicar_hex_digitado
        )
        aplicar_hex.setFixedWidth(90)

        hex_layout.addWidget(self.hex_input, 1)
        hex_layout.addWidget(aplicar_hex)

        textos.addWidget(hex_label)
        textos.addLayout(hex_layout)

        topo.addWidget(self.preview)
        topo.addLayout(textos, 1)

        painel_layout.addLayout(topo)

        grid = QGridLayout()
        grid.setSpacing(8)

        for index, cor in enumerate(CORES_PADRAO):
            botao = QPushButton()
            botao.setFixedSize(30, 30)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {cor};
                    border: 2px solid #ffffff;
                    border-radius: 15px;
                }}

                QPushButton:hover {{
                    border: 2px solid #0f172a;
                }}
                """
            )
            botao.clicked.connect(
                lambda checked=False, c=cor: self._selecionar_cor(c)
            )

            grid.addWidget(
                botao,
                index // 8,
                index % 8,
            )

        painel_layout.addLayout(grid)

        corpo.addWidget(painel, 1)

        lateral = QHBoxLayout()
        lateral.setSpacing(14)

        hue_coluna = QVBoxLayout()
        hue_coluna.setSpacing(8)

        self.hue_bar = HueBar()
        self.hue_bar.hue_changed.connect(
            self._selecionar_por_hue
        )

        hue_label = QLabel("Hue")
        hue_label.setAlignment(Qt.AlignCenter)

        hue_coluna.addWidget(hue_label)
        hue_coluna.addWidget(self.hue_bar)

        saturation_coluna = QVBoxLayout()
        saturation_coluna.setSpacing(8)

        self.saturation_bar = SaturationBar()
        self.saturation_bar.saturation_changed.connect(
            self._selecionar_por_saturacao
        )

        saturation_label = QLabel("Sat")
        saturation_label.setAlignment(Qt.AlignCenter)

        saturation_coluna.addWidget(saturation_label)
        saturation_coluna.addWidget(self.saturation_bar)

        lateral.addLayout(hue_coluna)
        lateral.addLayout(saturation_coluna)

        corpo.addLayout(lateral)

        layout.addLayout(corpo, 1)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        confirmar = QPushButton("Confirmar")
        confirmar.clicked.connect(self._confirmar)
        confirmar.setStyleSheet(
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

        botoes.addWidget(cancelar)
        botoes.addWidget(confirmar)

        layout.addLayout(botoes)

    def _selecionar_cor(
            self,
            cor: str,
    ) -> None:
        cor = cor.upper()

        self.cor_atual = cor
        self.preview.set_color(cor)
        self.hex_input.setText(cor)

        qcolor = QColor(cor)

        self.hue = qcolor.hue() if qcolor.hue() >= 0 else self.hue
        self.saturation = qcolor.saturation()
        self.value = qcolor.value()

        self.saturation_bar.hue = self.hue
        self.saturation_bar.saturation = self.saturation

        self.saturation_bar.update()

        if qcolor.isValid():
            self.hue_bar.hue = qcolor.hue() if qcolor.hue() >= 0 else 0
            self.hue_bar.update()

    def _selecionar_por_hue(
            self,
            hue: int,
    ) -> None:
        self.hue = hue

        self.saturation_bar.hue = hue
        self.saturation_bar.update()

        cor = QColor.fromHsv(
            self.hue,
            self.saturation,
            self.value,
        ).name().upper()

        self._selecionar_cor(cor)

    def _selecionar_por_saturacao(
            self,
            saturation: int,
    ) -> None:
        self.saturation = saturation

        cor = QColor.fromHsv(
            self.hue,
            self.saturation,
            self.value,
        ).name().upper()

        self._selecionar_cor(cor)

    def _aplicar_hex_digitado(self) -> None:
        cor = self.hex_input.text().strip().upper()

        if not cor.startswith("#"):
            cor = f"#{cor}"

        if not QColor(cor).isValid() or len(cor) != 7:
            self.hex_input.setText(self.cor_atual)
            return

        self._selecionar_cor(cor)

    def _confirmar(self) -> None:
        self.resultado = self.cor_atual
        self.accept()


def escolher_cor(
        parent=None,
        cor_inicial: str = "#7C3AED",
) -> str | None:
    dialog = ColorPickerDialog(
        cor_inicial=cor_inicial,
        parent=parent,
    )

    if dialog.exec() == QDialog.Accepted:
        return dialog.resultado

    return None