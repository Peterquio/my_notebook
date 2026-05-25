from PySide6.QtWidgets import QMessageBox
from ui.dialogs.card_catalog_dialog import CardCatalogDialog

class DashboardCardCatalogController:
    def __init__(
            self,
            parent,
            module_name: str,
            catalog_provider,
            card_generator,
            card_data_factory,
            dashboard_area,
            dashboard_card_service,
            on_slot_created=None,
    ) -> None:

        self.parent = parent
        self.module_name = module_name
        self.catalog_provider = catalog_provider
        self.card_generator = card_generator
        self.card_data_factory = card_data_factory
        self.dashboard_area = dashboard_area
        self.dashboard_card_service = dashboard_card_service
        self.card_catalog_dialog = None
        self.on_slot_created = on_slot_created

    def abrir_seletor_cards(self) -> None:
        cards_removidos = self.dashboard_card_service.listar_cards_removidos(
            module_name=self.module_name
        )

        self.card_catalog_dialog = CardCatalogDialog(
            self.catalog_provider(),
            removed_cards=cards_removidos,
            parent=self.parent,
        )

        self.card_catalog_dialog.card_selected.connect(
            self._processar_card_selecionado
        )

        self.card_catalog_dialog.preview_requested.connect(
            self._visualizar_card_removido
        )

        self.card_catalog_dialog.delete_requested.connect(
            self._confirmar_exclusao_card_removido
        )

        self.card_catalog_dialog.exec()

    def _processar_card_selecionado(
            self,
            card_data: dict,
    ) -> None:

        if card_data.get("is_active") == 0:
            self._readicionar_card_removido(card_data)
            return

        self._adicionar_card_novo(card_data)

    def _adicionar_card_novo(
            self,
            card_data: dict,
    ) -> None:

        card_data = self.card_data_factory(
            card_data
        )

        self.dashboard_card_service.criar_card(
            module_name=self.module_name,
            card_data=card_data,
        )

        slot = self.card_generator(
            card_data
        )

        self._finalizar_slot(slot)

        self.dashboard_area.add_card(
            slot,
            size=card_data.get("size", "1x1"),
        )

        slot.set_edit_mode(
            self.dashboard_area.dashboard_grid.edit_mode
        )

    def _readicionar_card_removido(
            self,
            card_data: dict,
    ) -> None:

        self.dashboard_card_service.reativar_card(
            card_data["id"]
        )

        slot = self.card_generator(
            card_data
        )

        self._finalizar_slot(slot)

        self.dashboard_area.add_card(
            slot,
            size=card_data.get("size", "1x1"),
        )

    def _visualizar_card_removido(
            self,
            card_data: dict,
    ) -> None:

        QMessageBox.information(
            self.parent,
            "Visualizar card",
            (
                f"Nome: {card_data.get('title', 'Card')}\n"
                f"Tipo: {card_data.get('card_type', '')}\n"
                f"Tamanho: {card_data.get('size', '')}\n"
                f"Configuração: {card_data.get('config', {})}"
            ),
        )

    def _confirmar_exclusao_card_removido(
            self,
            card_data: dict,
    ) -> None:

        resposta = QMessageBox.question(
            self.parent,
            "Excluir card definitivamente",
            (
                f"Deseja excluir definitivamente o card "
                f"'{card_data.get('title', 'Card')}'?\n\n"
                "Essa ação não poderá ser desfeita."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        self.dashboard_card_service.excluir_card_definitivamente(
            card_data["id"]
        )

        if self.card_catalog_dialog is not None:
            self.card_catalog_dialog.remover_card_da_lista(
                card_data["id"]
            )

        print(f"[DASHBOARD] Card excluído definitivamente: {card_data['id']}")

    def _finalizar_slot(
            self,
            slot,
    ) -> None:

        slot.delete_requested.connect(
            self.dashboard_card_service.remover_ou_desativar_card
        )

        if self.on_slot_created is not None:
            self.on_slot_created(slot)