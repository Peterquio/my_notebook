from modules.finance.repositories.finance_category_repository import (
    FinanceCategoryRepository,
)


class FinanceCategoryService:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.repository = FinanceCategoryRepository(username)

    def listar_categorias_ativas(self) -> list[dict]:
        return self.repository.listar_ativas()

    def criar_categoria(
            self,
            name: str,
            color: str,
    ) -> int:
        name = self._validar_nome(name)
        color = self._validar_cor(color)

        display_number = self.repository.obter_proximo_display_number()

        return self.repository.criar(
            name=name,
            color=color,
            display_number=display_number,
        )

    def atualizar_categoria(
            self,
            category_id: int,
            name: str,
            color: str,
            display_number: int,
    ) -> None:
        name = self._validar_nome(name)
        color = self._validar_cor(color)

        if display_number <= 0:
            raise ValueError("O número de exibição deve ser maior que zero.")

        self.repository.atualizar(
            category_id=category_id,
            name=name,
            color=color,
            display_number=display_number,
        )

    def desativar_categoria(
            self,
            category_id: int,
    ) -> None:
        if category_id == 1:
            raise ValueError("A categoria Outros não pode ser removida.")

        self.repository.desativar(category_id)

    def _validar_nome(
            self,
            name: str,
    ) -> str:
        name = name.strip()

        if not name:
            raise ValueError("Informe o nome da categoria.")

        if len(name) < 2:
            raise ValueError("O nome da categoria precisa ter pelo menos 2 caracteres.")

        return name

    def _validar_cor(
            self,
            color: str,
    ) -> str:
        color = color.strip()

        if not color.startswith("#") or len(color) != 7:
            raise ValueError("A cor deve estar no formato hexadecimal. Exemplo: #7C3AED")

        return color.upper()