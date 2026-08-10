from calendar import monthrange
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from modules.finance.repositories.finance_settings_repository import FinanceSettingsRepository
from modules.finance.repositories.pix_repository import PixRepository
from modules.finance.services.pix_balance_sync_service import PixBalanceSyncService

class PixService:
    TRANSACTION_TYPE_SENT = "sent"
    TRANSACTION_TYPE_RECEIVED = "received"

    VALID_TRANSACTION_TYPES = {
        TRANSACTION_TYPE_SENT,
        TRANSACTION_TYPE_RECEIVED,
    }

    MONTH_NAMES = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }

    def __init__(
            self,
            username: str,
    ) -> None:
        self.username = username

        self.repository = PixRepository(
            username
        )

        self.settings_repository = FinanceSettingsRepository(
            username
        )

        self.balance_sync_service = PixBalanceSyncService(
            username
        )

    def criar_transacao(
            self,
            account_id: int,
            transaction_type: str,
            amount_cents: int,
            transaction_date: str,
            contact_id: int | None = None,
            contact_name: str | None = None,
            category_id: int = 1,
            description: str | None = None,
            notes: str | None = None,
    ) -> int:

        account_id = self._validar_conta(
            account_id
        )

        transaction_type = self._validar_tipo(
            transaction_type
        )

        amount_cents = self._validar_valor(
            amount_cents
        )

        transaction_date = self._validar_data(
            transaction_date
        )

        contact_name = self._normalizar_texto(
            contact_name
        )

        description = self._normalizar_texto(
            description
        )

        notes = self._normalizar_texto(
            notes
        )

        transaction_id = self.repository.criar_transacao(
            account_id=account_id,
            transaction_type=transaction_type,
            amount_cents=amount_cents,
            transaction_date=transaction_date,
            contact_id=contact_id,
            contact_name=contact_name,
            category_id=category_id,
            description=description,
            notes=notes,
        )

        pix = self.repository.buscar_transacao_por_id(
            transaction_id
        )

        if pix is None:
            raise ValueError(
                "O PIX foi criado, mas não pôde ser carregado."
            )

        self.balance_sync_service.sincronizar(
            pix
        )

        return transaction_id

    def atualizar_transacao(
            self,
            transaction_id: int,
            account_id: int,
            transaction_type: str,
            amount_cents: int,
            transaction_date: str,
            contact_id: int | None = None,
            contact_name: str | None = None,
            category_id: int = 1,
            description: str | None = None,
            notes: str | None = None,
    ) -> None:

        if self.repository.buscar_transacao_por_id(
                transaction_id
        ) is None:
            raise ValueError(
                "Lançamento PIX não encontrado."
            )

        account_id = self._validar_conta(
            account_id
        )

        transaction_type = self._validar_tipo(
            transaction_type
        )

        amount_cents = self._validar_valor(
            amount_cents
        )

        transaction_date = self._validar_data(
            transaction_date
        )

        contact_name = self._normalizar_texto(
            contact_name
        )

        description = self._normalizar_texto(
            description
        )

        notes = self._normalizar_texto(
            notes
        )

        self.repository.atualizar_transacao(
            transaction_id=transaction_id,
            account_id=account_id,
            transaction_type=transaction_type,
            amount_cents=amount_cents,
            transaction_date=transaction_date,
            contact_id=contact_id,
            contact_name=contact_name,
            category_id=category_id,
            description=description,
            notes=notes,
        )

        pix = self.repository.buscar_transacao_por_id(
            transaction_id
        )

        if pix is None:
            raise ValueError(
                "O PIX foi atualizado, mas não pôde ser carregado."
            )

        self.balance_sync_service.sincronizar(
            pix
        )

    def excluir_transacao(
            self,
            transaction_id: int,
    ) -> None:

        if self.repository.buscar_transacao_por_id(
                transaction_id
        ) is None:
            raise ValueError(
                "Lançamento PIX não encontrado."
            )

        self.balance_sync_service.remover(
            transaction_id
        )

        self.repository.excluir_transacao(
            transaction_id
        )

    def buscar_transacao(
            self,
            transaction_id: int,
    ) -> dict | None:

        return self.repository.buscar_transacao_por_id(
            transaction_id
        )

    def listar_transacoes(
            self,
    ) -> list[dict]:

        return self.repository.listar_transacoes()

    def listar_transacoes_agrupadas_por_mes(
            self,
    ) -> list[dict]:

        transacoes = (
            self.repository.listar_transacoes()
        )

        grupos: dict[str, dict] = {}

        for transacao in transacoes:
            data = datetime.strptime(
                transacao["transaction_date"],
                "%Y-%m-%d",
            ).date()

            chave = (
                f"{data.year:04d}-"
                f"{data.month:02d}"
            )

            if chave not in grupos:
                grupos[chave] = {
                    "key": chave,
                    "year": data.year,
                    "month": data.month,
                    "month_name": self.MONTH_NAMES[
                        data.month
                    ],
                    "transactions": [],
                }

            grupos[chave][
                "transactions"
            ].append(
                transacao
            )

        return list(
            grupos.values()
        )

    def obter_resumo_mes(
            self,
            year: int | None = None,
            month: int | None = None,
    ) -> dict:

        hoje = date.today()

        if year is None:
            year = hoje.year

        if month is None:
            month = hoje.month

        ultimo_dia = monthrange(
            year,
            month,
        )[1]

        start_date = (
            f"{year:04d}-"
            f"{month:02d}-01"
        )

        end_date = (
            f"{year:04d}-"
            f"{month:02d}-"
            f"{ultimo_dia:02d}"
        )

        resumo = (
            self.repository
            .obter_resumo_periodo(
                start_date=start_date,
                end_date=end_date,
            )
        )

        return {
            "year": year,
            "month": month,
            "month_name": (
                self.MONTH_NAMES[month]
            ),
            "total_transactions": (
                resumo["total_transactions"]
                or 0
            ),
            "received_cents": (
                resumo["received_cents"]
                or 0
            ),
            "sent_cents": (
                resumo["sent_cents"]
                or 0
            ),
        }

    def obter_periodo_financeiro_atual(
            self,
    ) -> tuple[str, str]:

        reference_day = (
            self.settings_repository
            .obter_reference_day()
        )

        hoje = date.today()

        if hoje.day >= reference_day:
            ultimo_dia_mes = monthrange(
                hoje.year,
                hoje.month,
            )[1]

            dia_inicio = min(
                reference_day,
                ultimo_dia_mes,
            )

            inicio = hoje.replace(
                day=dia_inicio
            )

        else:
            mes_anterior = (
                hoje.replace(day=1)
                - relativedelta(months=1)
            )

            ultimo_dia_mes_anterior = (
                monthrange(
                    mes_anterior.year,
                    mes_anterior.month,
                )[1]
            )

            dia_inicio = min(
                reference_day,
                ultimo_dia_mes_anterior,
            )

            inicio = (
                mes_anterior.replace(
                    day=dia_inicio
                )
            )

        proximo_mes = (
            inicio
            + relativedelta(months=1)
        )

        fim = (
            proximo_mes
            - relativedelta(days=1)
        )

        return (
            inicio.isoformat(),
            fim.isoformat(),
        )

    def obter_resumo_periodo_atual(
            self,
    ) -> dict:

        start_date, end_date = (
            self.obter_periodo_financeiro_atual()
        )

        resumo = (
            self.repository
            .obter_resumo_periodo(
                start_date=start_date,
                end_date=end_date,
            )
        )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_transactions": (
                resumo["total_transactions"]
                or 0
            ),
            "sent_cents": (
                resumo["sent_cents"]
                or 0
            ),
            "received_cents": (
                resumo["received_cents"]
                or 0
            ),
        }

    def _validar_conta(
            self,
            account_id: int,
    ) -> int:

        if account_id is None:
            raise ValueError(
                "Selecione a conta do PIX."
            )

        try:
            account_id = int(
                account_id
            )
        except (TypeError, ValueError):
            raise ValueError(
                "A conta selecionada é inválida."
            )

        if account_id <= 0:
            raise ValueError(
                "A conta selecionada é inválida."
            )

        return account_id

    def _validar_tipo(
            self,
            transaction_type: str,
    ) -> str:

        transaction_type = (
            transaction_type
            or ""
        ).strip().lower()

        if (
            transaction_type
            not in self.VALID_TRANSACTION_TYPES
        ):
            raise ValueError(
                "Tipo de PIX inválido. "
                "Use 'sent' ou 'received'."
            )

        return transaction_type

    def _validar_valor(
            self,
            amount_cents: int,
    ) -> int:

        try:
            amount_cents = int(
                amount_cents
            )
        except (TypeError, ValueError):
            raise ValueError(
                "O valor do PIX é inválido."
            )

        if amount_cents <= 0:
            raise ValueError(
                "O valor do PIX deve ser maior que zero."
            )

        return amount_cents

    def _validar_data(
            self,
            transaction_date: str,
    ) -> str:

        try:
            data = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            )
        except (TypeError, ValueError):
            raise ValueError(
                "A data do PIX é inválida."
            )

        return data.strftime(
            "%Y-%m-%d"
        )

    def _normalizar_texto(
            self,
            texto: str | None,
    ) -> str | None:

        if texto is None:
            return None

        texto = texto.strip()

        if not texto:
            return None

        return texto