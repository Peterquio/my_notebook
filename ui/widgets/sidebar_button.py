#Botão da side bar

import customtkinter as ctk
from core.themes.theme_manager import theme

class SidebarButton(ctk.CTkButton):
    def __init__(
        self,
        master,
        text: str,
        command=None,
        selected: bool = False,
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            command=command,
            anchor="w",
            height=40,
            corner_radius=8,
            fg_color=self._get_fg_color(selected),
            hover_color=theme.sidebar_button_hover,
            text_color=theme.sidebar_button_text,
            **kwargs
        )

    def set_selected(self, selected: bool) -> None:
        self.configure(
            fg_color=self._get_fg_color(selected)
        )

    def _get_fg_color(self, selected: bool) -> str:
        if selected:
            return theme.sidebar_button_selected

        return theme.sidebar_button_transparent