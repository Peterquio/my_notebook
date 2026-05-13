import customtkinter as ctk

from ui.widgets.app_card import AppCard


class AddCardButton(AppCard):
    def __init__(
        self,
        master,
        command=None,
        width: int = 140,
        height: int = 120,
        **kwargs
    ):
        super().__init__(
            master,
            title="",
            value="+",
            subtitle="Adicionar card",
            icon="",
            variant="default",
            width=width,
            height=height,
            clickable=True,
            command=command,
            **kwargs
        )