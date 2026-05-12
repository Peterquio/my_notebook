import random
import customtkinter as ctk

from core.themes.theme_manager import theme
from core.themes.card_variants import CARD_VARIANTS


class AppCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str = "",
        variant: str = "default",
        width: int = 250,
        height: int = 140,
        **kwargs
    ):
        self.variant = self._resolver_variant(variant)

        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=self.variant["corner_radius"],
            fg_color=self.variant["fg_color"],
            border_color=self.variant["border_color"],
            border_width=self.variant["border_width"],
            **kwargs
        )

        self.grid_propagate(False)

        self._criar_widgets(title, value)

    def _resolver_variant(self, variant: str) -> dict:
        if variant == "random":
            variant_name = random.choice(list(CARD_VARIANTS.keys()))
            return theme.get_card_variant(variant_name)

        return theme.get_card_variant(variant)

    def _criar_widgets(self, title: str, value: str) -> None:
        titulo = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 15, "bold"),
            anchor="w",
            fg_color="transparent",
        )

        titulo.pack(
            anchor="w",
            padx=20,
            pady=(20, 5),
        )

        valor = ctk.CTkLabel(
            self,
            text=value,
            font=("Segoe UI", 28, "bold"),
            anchor="w",
            fg_color="transparent",
        )

        valor.pack(
            anchor="w",
            padx=20,
        )