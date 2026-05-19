class FocusModeController:
    def __init__(
            self,
            sidebar,
            content_stack,
    ) -> None:

        self.sidebar = sidebar
        self.content_stack = content_stack
        self.previous_widget = None
        self.focus_widget = None

    def enter_focus_mode(
            self,
            focus_widget,
    ) -> None:

        if self.focus_widget is not None:
            self.exit_focus_mode()

        self.previous_widget = self.content_stack.currentWidget()
        self.focus_widget = focus_widget

        self.sidebar.hide()

        self.content_stack.addWidget(
            self.focus_widget
        )

        self.content_stack.setCurrentWidget(
            self.focus_widget
        )

    def exit_focus_mode(self) -> None:
        if self.focus_widget is None:
            return

        if self.previous_widget is not None:
            self.content_stack.setCurrentWidget(
                self.previous_widget
            )

        self.content_stack.removeWidget(
            self.focus_widget
        )

        self.focus_widget.deleteLater()

        self.focus_widget = None
        self.previous_widget = None

        self.sidebar.show()