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
    preview_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(
            self,
            card_data: dict,
            show_actions: bool = False,
    ):
        super().__init__()

        self.card_data = card_data
        self.show_actions = show_actions

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

        subtitle = card_data.get("subtitle", "")

        if self.show_actions:
            subtitle = subtitle or f"ID: {card_data.get('id', '')[:8]}"

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("CardCatalogSubtitle")
        subtitle_label.setWordWrap(True)

        size_label = QLabel(card_data.get("size", "1x1"))
        size_label.setObjectName("CardCatalogSize")
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setFixedWidth(54)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        preview_button = QPushButton("Visualizar")
        preview_button.setObjectName("PrimarySoftButton")
        preview_button.setCursor(Qt.PointingHandCursor)
        preview_button.clicked.connect(
            lambda: self.preview_requested.emit(self.card_data)
        )

        delete_button = QPushButton("Excluir")
        delete_button.setObjectName("DangerSoftButton")
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(
            lambda: self.delete_requested.emit(self.card_data)
        )

        if self.show_actions:
            actions_layout.addWidget(preview_button)
            actions_layout.addWidget(delete_button)

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, stretch=1)
        layout.addWidget(size_label)

        if self.show_actions:
            layout.addLayout(actions_layout)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.card_data)
        super().mousePressEvent(event)


class CardCatalogDialog(QDialog):
    card_selected = Signal(dict)
    preview_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(
        self,
        cards: list[dict],
        removed_cards: list[dict] | None = None,
        parent=None,
        show_actions: bool = False,
    ):
        super().__init__(parent)

        self.cards = cards
        self.show_actions = show_actions
        self.removed_cards = removed_cards or []
        self.current_tab = None
        self.tab_buttons = {}

        self.setWindowTitle("Adicionar card")
        self.setModal(True)
        self.setMinimumSize(560, 520)
        self.setObjectName("CardCatalogDialog")

        self.setStyleSheet("""
            QPushButton#CatalogTabButton {
                background-color: #F1F5F9;
                color: #64748B;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
                padding: 10px 18px;
                font-weight: 700;
            }

            QPushButton#CatalogTabButton:checked {
                background-color: #EAF1FF;
                color: #2563EB;
                border: 1px solid #2563EB;
            }

            QPushButton#PrimarySoftButton {
                background-color: #EFF6FF;
                color: #2563EB;
                border: 1px solid #BFDBFE;
                border-radius: 12px;
                font-weight: 600;
                padding: 6px 14px;
            }

            QPushButton#PrimarySoftButton:hover {
                background-color: #DBEAFE;
            }

            QPushButton#DangerSoftButton {
                background-color: #FEF2F2;
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 12px;
                font-weight: 600;
                padding: 6px 14px;
            }

            QPushButton#DangerSoftButton:hover {
                background-color: #FEE2E2;
            }
        """)

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

        tabs_layout = QHBoxLayout()
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(10)

        self.tabs_layout = tabs_layout
        self._criar_abas_dinamicas()

        scroll = QScrollArea()
        scroll.setObjectName("CardCatalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("CardCatalogContent")

        self.cards_layout = QVBoxLayout(content)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)

        scroll.setWidget(content)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(tabs_layout)
        main_layout.addWidget(scroll)

        self._populate_cards()

    def _selecionar_card(self, card_data: dict) -> None:
        self.card_selected.emit(card_data)
        self.accept()

    def _switch_tab(
            self,
            tab_name: str,
    ) -> None:

        self.current_tab = tab_name

        for key, button in self.tab_buttons.items():
            button.setChecked(key == tab_name)

        self._populate_cards()

    def _clear_cards_layout(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _populate_cards(self) -> None:
        self._clear_cards_layout()

        if self.current_tab == "removed":
            cards = self.removed_cards
            show_actions = True
        else:
            cards = [
                card
                for card in self.cards
                if card.get("group", "module") == self.current_tab
            ]
            show_actions = False

        if not cards:
            empty_label = QLabel("Nenhum card disponível nesta aba.")
            empty_label.setObjectName("CardCatalogDialogSubtitle")
            empty_label.setAlignment(Qt.AlignCenter)

            self.cards_layout.addWidget(empty_label)
            self.cards_layout.addStretch()
            return

        for card_data in cards:
            item = CardCatalogItem(
                card_data,
                show_actions=show_actions,
            )

            item.clicked.connect(self._selecionar_card)
            item.preview_requested.connect(self.preview_requested.emit)
            item.delete_requested.connect(self.delete_requested.emit)

            self.cards_layout.addWidget(item)

        self.cards_layout.addStretch()

    def remover_card_da_lista(
            self,
            card_id: str,
    ) -> None:

        self.removed_cards = [
            card
            for card in self.removed_cards
            if card.get("id") != card_id
        ]

        if not self.removed_cards and "removed" in self.tab_buttons:
            button = self.tab_buttons.pop("removed")
            button.deleteLater()

            if self.current_tab == "removed":
                abas = self._obter_abas_disponiveis()

                if abas:
                    self.current_tab = abas[0]["key"]
                    self.tab_buttons[self.current_tab].setChecked(True)
                else:
                    self.current_tab = None

        if self.current_tab is not None:
            self._populate_cards()

    def _obter_abas_disponiveis(self) -> list[dict]:
        abas = []

        grupos = {
            card.get("group", "module")
            for card in self.cards
        }

        if "module" in grupos:
            abas.append({
                "key": "module",
                "label": "Módulos",
            })

        if "tool" in grupos:
            abas.append({
                "key": "tool",
                "label": "Ferramentas",
            })

        if self.removed_cards:
            abas.append({
                "key": "removed",
                "label": "Removidos",
            })

        return abas

    def _criar_abas_dinamicas(self) -> None:
        abas = self._obter_abas_disponiveis()

        for aba in abas:
            button = QPushButton(aba["label"])
            button.setObjectName("CatalogTabButton")
            button.setCheckable(True)
            button.setMinimumHeight(44)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, key=aba["key"]: self._switch_tab(key)
            )

            self.tab_buttons[aba["key"]] = button
            self.tabs_layout.addWidget(button)

        self.tabs_layout.addStretch()

        if abas:
            self.current_tab = abas[0]["key"]
            self.tab_buttons[self.current_tab].setChecked(True)