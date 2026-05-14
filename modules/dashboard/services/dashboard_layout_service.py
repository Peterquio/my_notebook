from core.database.database_manager import DatabaseManager
from modules.dashboard.repositories.dashboard_layout_repository import (
    DashboardLayoutRepository,
)


class DashboardLayoutService:
    def __init__(
        self,
        username: str,
    ):
        self.username = username

    def salvar_layout(
        self,
        module_name: str,
        layout_items: list[dict],
    ) -> None:

        database_manager = DatabaseManager(self.username)

        with database_manager.conectar() as conexao:
            repository = DashboardLayoutRepository(conexao)

            repository.salvar_layout(
                module_name,
                layout_items,
            )

    def carregar_layout(
        self,
        module_name: str,
    ) -> list[dict]:

        database_manager = DatabaseManager(self.username)

        with database_manager.conectar() as conexao:
            repository = DashboardLayoutRepository(conexao)

            return repository.listar_layout(
                module_name
            )