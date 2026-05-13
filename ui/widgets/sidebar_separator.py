import customtkinter as ctk

from core.themes import theme_tokens


class SidebarSeparator(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            width=150,
            height=3,
            corner_radius=0,
            fg_color=theme_tokens.SIDEBAR_SEPARATOR,
            **kwargs
        )

        self.pack_propagate(False)