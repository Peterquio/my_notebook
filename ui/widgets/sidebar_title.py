import customtkinter as ctk

from core.themes import theme_tokens


class SidebarTitle(ctk.CTkLabel):
    def __init__(
        self,
        master,
        text: str,
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            font=("Segoe UI", 22, "bold"),
            text_color=theme_tokens.SIDEBAR_BUTTON_TEXT,
            **kwargs
        )