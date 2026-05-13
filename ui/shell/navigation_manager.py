from PySide6.QtWidgets import QStackedWidget


class NavigationManager:
    def __init__(self, content_stack: QStackedWidget):
        self.content_stack = content_stack
        self.screens = {}

    def registrar_tela(self, nome: str, tela_factory) -> None:
        self.screens[nome] = {
            "factory": tela_factory,
            "instance": None,
        }

    def navegar_para(self, nome: str) -> None:
        if nome not in self.screens:
            raise ValueError(f"Tela não registrada: {nome}")

        tela_info = self.screens[nome]

        if tela_info["instance"] is None:
            tela = tela_info["factory"]()
            tela_info["instance"] = tela
            self.content_stack.addWidget(tela)

        self.content_stack.setCurrentWidget(tela_info["instance"])