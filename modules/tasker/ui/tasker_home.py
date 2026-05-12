from ui.widgets.base_screen import BaseScreen


class TaskerHome(BaseScreen):
    def __init__(self, master):
        super().__init__(
            master,
            title="Tasker",
            subtitle="Organize suas tarefas, rotinas e lembretes.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        pass