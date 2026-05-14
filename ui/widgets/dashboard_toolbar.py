from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget


class DashboardToolbar(QWidget):

    edit_mode_changed = Signal(bool)
    refresh_requested = Signal()
    cancel_requested = Signal()

    def __init__(self):
        super().__init__()

        self.edit_mode = False

        self._criar_layout()
        self._criar_widgets()

    def _criar_layout(self) -> None:
        self.layout = QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

    def _criar_widgets(self) -> None:
        self.refresh_button = QPushButton("🔄️")
        self.refresh_button.setObjectName("EditButton")

        self.cancel_button = QPushButton("❌")
        self.cancel_button.setObjectName("EditButton")
        self.cancel_button.hide()

        self.cancel_button.clicked.connect(
            self._cancel_edit_mode
        )

        self.edit_button = QPushButton("⚙️")
        self.edit_button.setObjectName("EditButton")

        self.edit_button.clicked.connect(
            self._toggle_edit_mode
        )

        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.cancel_button)
        self.layout.addWidget(self.edit_button)

    def _toggle_edit_mode(self) -> None:
        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            self.edit_button.setText("✅")
            self.cancel_button.show()
        else:
            self.edit_button.setText("⚙️")
            self.cancel_button.hide()

        self.edit_mode_changed.emit(
            self.edit_mode
        )

    def _cancel_edit_mode(self) -> None:
        self.edit_mode = False

        self.edit_button.setText("⚙️")
        self.cancel_button.hide()

        self.cancel_requested.emit()