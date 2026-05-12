#NÃO queremos destruir widgets toda hora
#NÃO queremos recriar telas gigantes
#queremos lazy loading
#queremos cache de telas
#queremos navegação modular profissional
#Esse arquivo é o cérebro da UI.

import customtkinter as ctk


class NavigationManager:
    def __init__(self, content_frame: ctk.CTkFrame):
        self.content_frame = content_frame
        self.screens = {}

    def registrar_tela(self, nome: str, tela_factory) -> None:
        self.screens[nome] = {
            "factory": tela_factory,
            "instance": None,
        }

    def navegar_para(self, nome: str) -> None:
        if nome not in self.screens:
            raise ValueError(f"Tela não registrada: {nome}")

        for widget in self.content_frame.winfo_children():
            widget.grid_forget()

        tela_info = self.screens[nome]

        if tela_info["instance"] is None:
            tela_info["instance"] = tela_info["factory"](self.content_frame)

        tela = tela_info["instance"]
        tela.grid(row=0, column=0, sticky="nsew")