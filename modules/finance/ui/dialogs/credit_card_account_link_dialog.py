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


class AccountLinkItem(QFrame):
    clicked = Signal(dict)

    def __init__(
            self,
            account_data: dict,
            selected: bool = False,
    ):
        super().__init__()

        self.account_data = account_data
        self.setObjectName("CardCatalogItem")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(16)

        icon_label = QLabel("🏦")
        icon_label.setObjectName("CardCatalogIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(52, 52)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel(account_data.get("name", "Conta"))
        title_label.setObjectName("CardCatalogTitle")

        institution = account_data.get("institution_name") or "Sem instituição"
        account_number = account_data.get("account_number") or "Sem número"

        subtitle_label = QLabel(
            f"{institution} • {account_number}"
        )
        subtitle_label.setObjectName("CardCatalogSubtitle")
        subtitle_label.setWordWrap(True)

        status_label = QLabel("Selecionada" if selected else "Vincular")
        status_label.setObjectName("CardCatalogSize")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFixedWidth(90)

        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, stretch=1)
        layout.addWidget(status_label)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.account_data)
        super().mousePressEvent(event)


class CreditCardAccountLinkDialog(QDialog):
    account_selected = Signal(dict)

    def __init__(
            self,
            accounts: list[dict],
            current_account_id: int | None = None,
            parent=None,
    ):
        super().__init__(parent)

        self.accounts = accounts
        self.current_account_id = current_account_id

        self.setWindowTitle("Vincular conta")
        self.setModal(True)
        self.setMinimumSize(560, 520)
        self.setObjectName("CardCatalogDialog")

        self._criar_layout()

    def _criar_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        header_layout = QHBoxLayout()

        title_area = QVBoxLayout()
        title_area.setSpacing(4)

        title_label = QLabel("Vincular cartão a uma conta")
        title_label.setObjectName("CardCatalogDialogTitle")

        subtitle_label = QLabel(
            "Escolha a conta que receberá os compromissos gerados pela fatura."
        )
        subtitle_label.setObjectName("CardCatalogDialogSubtitle")
        subtitle_label.setWordWrap(True)

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

        self.accounts_layout = QVBoxLayout(content)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(12)

        scroll.setWidget(content)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(scroll)

        self._popular_contas()

    def _popular_contas(self) -> None:
        if not self.accounts:
            empty_label = QLabel("Nenhuma conta cadastrada.")
            empty_label.setObjectName("CardCatalogDialogSubtitle")
            empty_label.setAlignment(Qt.AlignCenter)

            self.accounts_layout.addWidget(empty_label)
            self.accounts_layout.addStretch()
            return

        for account in self.accounts:
            item = AccountLinkItem(
                account_data=account,
                selected=account["id"] == self.current_account_id,
            )

            item.clicked.connect(self._selecionar_conta)

            self.accounts_layout.addWidget(item)

        self.accounts_layout.addStretch()

    def _selecionar_conta(
            self,
            account_data: dict,
    ) -> None:
        self.account_selected.emit(account_data)
        self.accept()