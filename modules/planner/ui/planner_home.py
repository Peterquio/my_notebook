from ui.widgets.base_screen import BaseScreen


class PlannerHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Planner",
            subtitle="Planeje metas, projetos e compromissos.",
        )