from ui.widgets.base_screen import BaseScreen


class PlannerHome(BaseScreen):
    def __init__(self, master):
        super().__init__(
            master,
            title="Planner",
            subtitle="Planeje metas, projetos e compromissos.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        pass