from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)


class CardCatalogItem(QFrame):
    clicked = Signal(dict)

    def __init__(self, card_data: dict):
        super().__init__()

        self.card_data = card_data

        self.setObjectName("CardCatalogItem")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        icon_label = QLabel(card_data.get("icon", "◻"))
        icon_label.setObjectName("CardCatalogIcon")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(card_data.get("title", "Card"))
        title_label.setObjectName("CardCatalogTitle")

        subtitle_label = QLabel(card_data.get("subtitle", ""))
        subtitle_label.setObjectName("CardCatalogSubtitle")

        size_label = QLabel(f"Tamanho: {card_data.get('size', '1x1')}")
        size_label.setObjectName("CardCatalogSize")

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        text_layout.addWidget(size_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.card_data)
        super().mousePressEvent(event)


class CardCatalogDialog(QDialog):
    card_selected = Signal(dict)

    def __init__(
        self,
        cards: list[dict],
        parent=None,
    ):
        super().__init__(parent)

        self.cards = cards

        self.setWindowTitle("Adicionar card")
        self.setModal(True)
        self.setMinimumWidth(420)

        self._criar_layout()

    def _criar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("Escolha um card")
        title_label.setObjectName("DialogTitle")

        layout.addWidget(title_label)

        for card_data in self.cards:
            item = CardCatalogItem(card_data)
            item.clicked.connect(self._selecionar_card)

            layout.addWidget(item)

    def _selecionar_card(self, card_data: dict) -> None:
        self.card_selected.emit(card_data)
        self.accept()