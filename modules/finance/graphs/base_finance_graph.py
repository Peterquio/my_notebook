from abc import ABC, abstractmethod


class BaseFinanceGraph(ABC):
    graph_id: str = ""
    title: str = ""

    def __init__(
            self,
            username: str,
    ) -> None:

        self.username = username

    @abstractmethod
    def carregar_dados(
            self,
            start_date: str,
            end_date: str,
    ) -> dict:
        raise NotImplementedError