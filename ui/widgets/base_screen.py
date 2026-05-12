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

        self.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._criar_cabecalho(title, subtitle)
        self._criar_content_area()

    def _criar_cabecalho(self, title: str, subtitle: str) -> None:
        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(30, 20),
        )

        titulo = ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Segoe UI", 28, "bold"),
            anchor="w",
        )

        titulo.pack(anchor="w")

        if subtitle:
            subtitulo = ctk.CTkLabel(
                header_frame,
                text=subtitle,
                font=("Segoe UI", 14),
                anchor="w",
            )

            subtitulo.pack(anchor="w", pady=(5, 0))

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