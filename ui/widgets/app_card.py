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
        subtitle: str = "",
        icon: str = "",
        variant: str = "default",
        width: int = 250,
        height: int = 160,
        clickable: bool = False,
        command=None,
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
        self.pack_propagate(False)

        self.clickable = clickable
        self.command = command

        self._criar_widgets(
            title,
            value,
            subtitle,
            icon,
        )

        if clickable:
            self._configurar_hover()

    def _resolver_variant(self, variant: str) -> dict:
        if variant == "random":
            variant_name = random.choice(
                list(CARD_VARIANTS.keys())
            )

            return theme.get_card_variant(variant_name)

        return theme.get_card_variant(variant)

    def _criar_widgets(
        self,
        title: str,
        value: str,
        subtitle: str,
        icon: str,
    ) -> None:

        top_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        top_frame.pack(
            fill="x",
            padx=20,
            pady=(18, 8),
        )

        titulo = ctk.CTkLabel(
            top_frame,
            text=title,
            font=("Segoe UI", 15, "bold"),
            anchor="w",
        )

        titulo.pack(side="left")

        valor = ctk.CTkLabel(
            self,
            text=value,
            font=("Segoe UI", 30, "bold"),
            anchor="w",
        )

        valor.pack(
            anchor="w",
            padx=20,
        )

        if subtitle:
            subtitulo = ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Segoe UI", 13),
                anchor="w",
            )

            subtitulo.pack(
                anchor="w",
                padx=20,
                pady=(6, 0),
            )

        bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        bottom_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 12),
        )

        if icon:
            icone = ctk.CTkLabel(
                bottom_frame,
                text=icon,
                font=("Segoe UI Emoji", 24),
            )

            icone.pack(
                anchor="se",
                side="right",
            )

    def _configurar_hover(self) -> None:
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event) -> None:
        self.configure(border_width=3)

    def _on_leave(self, event) -> None:
        self.configure(
            border_width=self.variant["border_width"]
        )

    def _on_click(self, event) -> None:
        if self.command:
            self.command()