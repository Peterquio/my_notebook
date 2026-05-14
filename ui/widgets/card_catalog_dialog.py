from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QWidget,
    QPushButton,
)


class CardCatalogItem(QFrame):
    clicked = Signal(dict)

    def __init__(self, card_data: dict):
        super().__init__()

        self.card_data = card_data

        self.setObjectName("CardCatalogItem")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(16)

        icon_label = QLabel(card_data.get("icon", "◻"))
        icon_label.setObjectName("CardCatalogIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(52, 52)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel(card_data.get("title", "Card"))
        title_label.setObjectName("CardCatalogTitle")

        subtitle_label = QLabel(card_data.get("subtitle", ""))
        subtitle_label.setObjectName("CardCatalogSubtitle")
        subtitle_label.setWordWrap(True)

        size_label = QLabel(card_data.get("size", "1x1"))
        size_label.setObjectName("CardCatalogSize")
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setFixedWidth(54)

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, stretch=1)
        layout.addWidget(size_label)

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
        self.setMinimumSize(560, 520)
        self.setObjectName("CardCatalogDialog")

        self._criar_layout()

    def _criar_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_area = QVBoxLayout()
        title_area.setSpacing(4)

        title_label = QLabel("Adicionar card")
        title_label.setObjectName("CardCatalogDialogTitle")

        subtitle_label = QLabel("Escolha um card disponível para este módulo.")
        subtitle_label.setObjectName("CardCatalogDialogSubtitle")

        title_area.addWidget(title_label)
        title_area.addWidget(subtitle_label)

        close_button = QPushButton("×")
        close_button.setObjectName("CardCatalogCloseButton")
        close_button.setFixedSize(34, 34)
        close_button.clicked.connect(self.reject)

        header_layout.addLayout(title_area)
        header_layout.addStretch()
        header_layout.addWidget(close_button)

        scroll = QScrollArea()
        scroll.setObjectName("CardCatalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("CardCatalogContent")

        cards_layout = QVBoxLayout(content)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(12)

        for card_data in self.cards:
            item = CardCatalogItem(card_data)
            item.clicked.connect(self._selecionar_card)

            cards_layout.addWidget(item)

        cards_layout.addStretch()

        scroll.setWidget(content)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll)

    def _selecionar_card(self, card_data: dict) -> None:
        self.card_selected.emit(card_data)
        self.accept()