from ui.widgets.base_screen import BaseScreen


class FinanceHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Financeiro",
            subtitle="Controle suas receitas, despesas, cartões e categorias.",
        )