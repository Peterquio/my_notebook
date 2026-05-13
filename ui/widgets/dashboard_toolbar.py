import customtkinter as ctk


class DashboardToolbar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_toggle_edit,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )

        self.edit_mode = False
        self.on_toggle_edit = on_toggle_edit

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        self.edit_button = ctk.CTkButton(
            self,
            text="⚙",
            width=42,
            height=42,
            corner_radius=12,
            command=self._toggle_edit_mode,
        )

        self.edit_button.pack(
            side="right",
        )

    def _toggle_edit_mode(self) -> None:
        self.edit_mode = not self.edit_mode

        self.on_toggle_edit(self.edit_mode)

        if self.edit_mode:
            self.edit_button.configure(
                text="✔"
            )
        else:
            self.edit_button.configure(
                text="⚙"
            )