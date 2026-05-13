import customtkinter as ctk
import tkinter as tk

class EditableCardGrid(ctk.CTkFrame):
    def __init__(
        self,
        master,
        columns: int = 4,
        unit_width: int = 140,
        unit_height: int = 120,
        spacing: int = 15,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.columns = columns
        self.unit_width = unit_width
        self.unit_height = unit_height
        self.spacing = spacing
        self.edit_mode = False
        self.hover_overlay = None

        self.occupied_cells = []
        self.cards = []
        self.grid_canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
            bg="#f8fafc",
        )

        self.bind("<Configure>", self._on_resize)

    def add_card(
        self,
        card,
        size: str = "1x1",
    ) -> None:
        width_units, height_units = self._parse_size(size)

        row, column = self._find_available_position(
            width_units,
            height_units,
        )

        self._mark_cells_as_occupied(
            row,
            column,
            width_units,
            height_units,
        )

        card.configure(
            width=self._calculate_width(width_units),
            height=self._calculate_height(height_units),
        )

        card.grid(
            row=row,
            column=column,
            columnspan=width_units,
            rowspan=height_units,
            padx=self.spacing,
            pady=self.spacing,
            sticky="nsew",
        )
        self.cards.append(card)
        self._bind_card_hover(card)

    def _parse_size(self, size: str) -> tuple[int, int]:
        width, height = size.lower().split("x")

        return int(width), int(height)

    def _find_available_position(
        self,
        width_units: int,
        height_units: int,
    ) -> tuple[int, int]:
        row = 0

        while True:
            for column in range(self.columns):
                if self._can_place_card(
                    row,
                    column,
                    width_units,
                    height_units,
                ):
                    return row, column

            row += 1

    def _can_place_card(
        self,
        row: int,
        column: int,
        width_units: int,
        height_units: int,
    ) -> bool:
        if column + width_units > self.columns:
            return False

        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                if (r, c) in self.occupied_cells:
                    return False

        return True

    def _mark_cells_as_occupied(
        self,
        row: int,
        column: int,
        width_units: int,
        height_units: int,
    ) -> None:
        for r in range(row, row + height_units):
            for c in range(column, column + width_units):
                self.occupied_cells.append((r, c))

    def _calculate_width(self, units: int) -> int:
        return (self.unit_width * units) + (
            self.spacing * 2 * (units - 1)
        )

    def _calculate_height(self, units: int) -> int:
        return (self.unit_height * units) + (
            self.spacing * 2 * (units - 1)
        )

    def set_edit_mode(self, enabled: bool) -> None:
        self.edit_mode = enabled

        for card in self.cards:
            if hasattr(card, "set_edit_mode"):
                card.set_edit_mode(enabled)

        if enabled:
            self.configure(
                fg_color="#f8fafc",
            )

            self.grid_canvas.place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1,
            )

            self._draw_grid_points()

        else:
            self.configure(
                fg_color="transparent",
            )

            self.grid_canvas.place_forget()

    def _on_resize(self, event) -> None:
        if self.edit_mode:
            self._draw_grid_points()

    def _draw_grid_points(self) -> None:
        self.grid_canvas.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()

        spacing_x = self.unit_width + (self.spacing * 2)
        spacing_y = self.unit_height + (self.spacing * 2)

        point_radius = 2

        for y in range(0, height, spacing_y):
            for x in range(0, width, spacing_x):
                self.grid_canvas.create_oval(
                    x - point_radius,
                    y - point_radius,
                    x + point_radius,
                    y + point_radius,
                    fill="#cbd5e1",
                    outline="",
                )

    def _show_hover_overlay(self, card) -> None:
        if not self.edit_mode:
            return

        self._hide_hover_overlay()

        card.update_idletasks()

        x = card.winfo_x()
        y = card.winfo_y()
        width = card.winfo_width()
        height = card.winfo_height()

        extra_width = int(width * 0.04)
        extra_height = int(height * 0.04)

        self.hover_overlay = ctk.CTkFrame(
            self,
            width=width + extra_width,
            height=height + extra_height,
            corner_radius=card.variant["corner_radius"] + 6,
            fg_color="transparent",
            border_color="#94a3b8",
            border_width=2,
        )

        self.hover_overlay.place(
            x=x - extra_width // 2,
            y=y - extra_height // 2,
        )

        self.hover_overlay.lower(card)

    def _hide_hover_overlay(self) -> None:
        if self.hover_overlay is not None:
            self.hover_overlay.destroy()
            self.hover_overlay = None

    def _bind_card_hover(self, card) -> None:
        widgets = [card]

        for child in card.winfo_children():
            widgets.append(child)

            for nested_child in child.winfo_children():
                widgets.append(nested_child)

        for widget in widgets:
            widget.bind(
                "<Enter>",
                lambda event, c=card: self._show_hover_overlay(c),
                add="+",
            )

            widget.bind(
                "<Leave>",
                lambda event, c=card: self._schedule_hide_hover_overlay(c),
                add="+",
            )

    def _schedule_hide_hover_overlay(self, card) -> None:
        self.after(
            80,
            lambda: self._hide_hover_overlay_if_mouse_left(card),
        )

    def _hide_hover_overlay_if_mouse_left(self, card) -> None:
        if not self._mouse_is_inside(card):
            self._hide_hover_overlay()

    def _mouse_is_inside(self, widget) -> bool:
        pointer_x = widget.winfo_pointerx()
        pointer_y = widget.winfo_pointery()

        widget_x = widget.winfo_rootx()
        widget_y = widget.winfo_rooty()
        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()

        return (
                widget_x <= pointer_x <= widget_x + widget_width
                and widget_y <= pointer_y <= widget_y + widget_height
        )