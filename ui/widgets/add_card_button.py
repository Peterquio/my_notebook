from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class AddCardButton(QFrame):
    clicked = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName("AddCardButton")
        self.setCursor(Qt.PointingHandCursor)

        self._criar_shadow()
        self._criar_layout()

    def _criar_shadow(self) -> None:
        self.shadow = QGraphicsDropShadowEffect()

        self.shadow.setBlurRadius(8)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 18))

        self.setGraphicsEffect(self.shadow)

    def _criar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        plus_label = QLabel("+")
        plus_label.setObjectName("AddCardPlus")
        plus_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel("Adicionar card")
        text_label.setObjectName("AddCardText")
        text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(plus_label)
        layout.addWidget(text_label)

    def set_base_size(
        self,
        width: int,
        height: int,
    ) -> None:
        self.setFixedSize(width, height)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)