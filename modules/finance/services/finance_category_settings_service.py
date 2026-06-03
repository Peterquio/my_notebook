import json
from pathlib import Path

from modules.finance.repositories.finance_category_repository import (
    FinanceCategoryRepository,
)
from modules.finance.services.finance_category_service import (
    FinanceCategoryService,
)


class FinanceCategorySettingsService:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.repository = FinanceCategoryRepository(username)
        self.category_service = FinanceCategoryService(username)

    def exportar_categorias(
            self,
            caminho_arquivo: str | Path,
    ) -> dict:
        caminho_arquivo = Path(caminho_arquivo)

        categorias = self.repository.listar_todas()

        categorias_exportadas = []

        for categoria in categorias:
            if categoria["is_protected"]:
                continue

            categorias_exportadas.append(
                {
                    "display_number": categoria["display_number"],
                    "name": categoria["name"],
                    "color": categoria["color"],
                    "is_active": categoria["is_active"],
                }
            )

        dados = {
            "type": "my_notebook.finance.categories",
            "version": 1,
            "categories": categorias_exportadas,
        }

        caminho_arquivo.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4,
            )

        return {
            "exportadas": len(categorias_exportadas),
            "arquivo": str(caminho_arquivo),
        }

    def importar_categorias(
            self,
            caminho_arquivo: str | Path,
            substituir: bool = False,
    ) -> dict:
        caminho_arquivo = Path(caminho_arquivo)

        if not caminho_arquivo.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho_arquivo}"
            )

        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if dados.get("type") != "my_notebook.finance.categories":
            raise ValueError(
                "O arquivo informado não é um arquivo válido de categorias do My Notebook."
            )

        if dados.get("version") != 1:
            raise ValueError(
                "Versão de arquivo de categorias não suportada."
            )

        categorias_importadas = dados.get("categories", [])

        if not isinstance(categorias_importadas, list):
            raise ValueError(
                "O campo 'categories' precisa ser uma lista."
            )

        criadas = 0
        atualizadas = 0
        reativadas = 0
        desativadas = 0

        nomes_importados = set()

        for categoria in categorias_importadas:
            name = self.category_service._validar_nome(
                str(categoria.get("name", ""))
            )

            color = self.category_service._validar_cor(
                str(categoria.get("color", "#94A3B8"))
            )

            display_number = int(
                categoria.get("display_number", 0)
            )

            is_active = int(
                categoria.get("is_active", 1)
            )

            if display_number <= 0:
                raise ValueError(
                    f"A categoria '{name}' possui display_number inválido."
                )

            nomes_importados.add(
                name.strip().lower()
            )

            categoria_existente = self.repository.buscar_por_nome(
                name
            )

            if categoria_existente is None:
                category_id = self.repository.criar(
                    name=name,
                    color=color,
                    display_number=display_number,
                )

                criadas += 1

                if not is_active:
                    self.repository.desativar(
                        category_id
                    )

                continue

            if categoria_existente["is_protected"]:
                continue

            self.repository.atualizar(
                category_id=categoria_existente["id"],
                name=name,
                color=color,
                display_number=display_number,
            )

            atualizadas += 1

            if is_active and not categoria_existente["is_active"]:
                self.repository.reativar(
                    category_id=categoria_existente["id"],
                    display_number=display_number,
                )

                reativadas += 1

            if not is_active and categoria_existente["is_active"]:
                self.repository.desativar(
                    categoria_existente["id"]
                )

                desativadas += 1

        if substituir:
            categorias_atuais = self.repository.listar_todas()

            for categoria_atual in categorias_atuais:
                if categoria_atual["is_protected"]:
                    continue

                nome_atual = categoria_atual["name"].strip().lower()

                if nome_atual in nomes_importados:
                    continue

                if not categoria_atual["is_active"]:
                    continue

                self.repository.desativar(
                    categoria_atual["id"]
                )

                desativadas += 1

        return {
            "criadas": criadas,
            "atualizadas": atualizadas,
            "reativadas": reativadas,
            "desativadas": desativadas,
        }