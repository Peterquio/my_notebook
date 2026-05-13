from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel


class BaseScreen(QWidget):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
    ):
        super().__init__()

        self.edit_mode = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        self.header_layout = QHBoxLayout()
        self.title_area = QVBoxLayout()
        self.header_actions = QHBoxLayout()

        self.title_label = QLabel(title)
        self.title_label.setObjectName("ScreenTitle")

        self.title_area.addWidget(self.title_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("ScreenSubtitle")
            self.title_area.addWidget(self.subtitle_label)

        self.header_layout.addLayout(self.title_area)
        self.header_layout.addStretch()
        self.header_layout.addLayout(self.header_actions)

        self.content_area = QWidget()
        self.content_area.setObjectName("ScreenContent")

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.content_area)

    def set_edit_mode(self, enabled: bool) -> None:
        self.edit_mode = enabled

        if enabled:
            self.setProperty("editMode", True)
        else:
            self.setProperty("editMode", False)

        self.style().unpolish(self)
        self.style().polish(self)