from ui.widgets.base_screen import BaseScreen


class TaskerHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Tasker",
            subtitle="Organize suas tarefas, rotinas e lembretes.",
        )