import customtkinter as ctk


class BaseScreen(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        subtitle: str = "",
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=0,
            **kwargs
        )

        self.edit_mode = False

        self.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._criar_cabecalho(title, subtitle)
        self._criar_content_area()

    def _criar_cabecalho(self, title: str, subtitle: str) -> None:
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(30, 20),
        )

        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        text_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent",
        )

        text_frame.grid(
            row=0,
            column=0,
            sticky="w",
        )

        titulo = ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Segoe UI", 28, "bold"),
            anchor="w",
        )

        titulo.pack(anchor="w")

        if subtitle:
            subtitulo = ctk.CTkLabel(
                text_frame,
                text=subtitle,
                font=("Segoe UI", 14),
                anchor="w",
            )

            subtitulo.pack(anchor="w", pady=(5, 0))

        self.header_actions = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent",
        )

        self.header_actions.grid(
            row=0,
            column=1,
            sticky="e",
        )

    def _criar_content_area(self) -> None:
        self.content_area = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        self.content_area.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 30),
        )

        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def set_edit_mode(self, enabled: bool) -> None:
        self.edit_mode = enabled

        if enabled:
            self.configure(fg_color="#f8fafc")
            self.content_area.configure(fg_color="#f8fafc")
        else:
            self.configure(fg_color="transparent")
            self.content_area.configure(fg_color="transparent")