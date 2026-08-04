from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
    QSizePolicy,
)

from core.cloud.google_drive.auth.google_auth_service import (
    GoogleAuthService,
)


class SettingsSection(QFrame):
    def __init__(
        self,
        title: str,
        description: str,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("SettingsSection")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )
        self.main_layout.setSpacing(14)

        title_label = QLabel(title)
        title_label.setObjectName(
            "SettingsSectionTitle"
        )

        description_label = QLabel(description)
        description_label.setObjectName(
            "SettingsSectionDescription"
        )
        description_label.setWordWrap(True)

        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(
            description_label
        )


class GoogleDriveSettingsSection(
    SettingsSection
):
    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(
            title="Google Drive",
            description=(
                "Conecte sua conta Google para "
                "armazenar backups do banco de dados "
                "do My Notebook."
            ),
            parent=parent,
        )

        self.auth_service = GoogleAuthService()

        self._criar_interface()
        self._atualizar_estado()

    def _criar_interface(self) -> None:
        status_container = QFrame()
        status_container.setObjectName(
            "SettingsStatusContainer"
        )

        status_layout = QHBoxLayout(
            status_container
        )
        status_layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )
        status_layout.setSpacing(10)

        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(
            10,
            10,
        )

        self.status_label = QLabel()
        self.status_label.setObjectName(
            "SettingsStatusLabel"
        )

        status_layout.addWidget(
            self.status_indicator
        )
        status_layout.addWidget(
            self.status_label
        )
        status_layout.addStretch()

        self.main_layout.addWidget(
            status_container
        )

        backup_info = QFrame()
        backup_info.setObjectName(
            "SettingsBackupInfo"
        )

        backup_info_layout = QVBoxLayout(
            backup_info
        )
        backup_info_layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )
        backup_info_layout.setSpacing(6)

        self.last_backup_label = QLabel(
            "Último backup: ainda não realizado"
        )
        self.last_backup_label.setObjectName(
            "SettingsInfoLabel"
        )

        self.remote_file_label = QLabel(
            "Arquivo remoto: não encontrado"
        )
        self.remote_file_label.setObjectName(
            "SettingsInfoLabel"
        )

        backup_info_layout.addWidget(
            self.last_backup_label
        )
        backup_info_layout.addWidget(
            self.remote_file_label
        )

        self.main_layout.addWidget(
            backup_info
        )

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.connect_button = QPushButton()
        self.connect_button.setObjectName(
            "SettingsPrimaryButton"
        )
        self.connect_button.clicked.connect(
            self._alternar_conexao
        )

        self.backup_button = QPushButton(
            "Fazer backup agora"
        )
        self.backup_button.setObjectName(
            "SettingsSecondaryButton"
        )
        self.backup_button.clicked.connect(
            self._backup_ainda_nao_integrado
        )

        self.restore_button = QPushButton(
            "Restaurar backup"
        )
        self.restore_button.setObjectName(
            "SettingsSecondaryButton"
        )
        self.restore_button.clicked.connect(
            self._restauracao_ainda_nao_integrada
        )

        buttons_layout.addWidget(
            self.connect_button
        )
        buttons_layout.addWidget(
            self.backup_button
        )
        buttons_layout.addWidget(
            self.restore_button
        )
        buttons_layout.addStretch()

        self.main_layout.addLayout(
            buttons_layout
        )

    def _atualizar_estado(self) -> None:
        conectado = (
            self.auth_service.esta_conectado()
        )

        if conectado:
            self.status_indicator.setStyleSheet(
                """
                background-color: #22c55e;
                border-radius: 5px;
                """
            )

            self.status_label.setText(
                "Conectado ao Google Drive"
            )

            self.connect_button.setText(
                "Desconectar"
            )

            self.connect_button.setObjectName(
                "SettingsDangerButton"
            )

        else:
            self.status_indicator.setStyleSheet(
                """
                background-color: #94a3b8;
                border-radius: 5px;
                """
            )

            self.status_label.setText(
                "Google Drive não conectado"
            )

            self.connect_button.setText(
                "Conectar ao Google Drive"
            )

            self.connect_button.setObjectName(
                "SettingsPrimaryButton"
            )

        self.connect_button.style().unpolish(
            self.connect_button
        )
        self.connect_button.style().polish(
            self.connect_button
        )

        self.backup_button.setEnabled(
            conectado
        )
        self.restore_button.setEnabled(
            conectado
        )

    def _alternar_conexao(self) -> None:
        if self.auth_service.esta_conectado():
            resposta = QMessageBox.question(
                self,
                "Desconectar Google Drive",
                (
                    "Deseja remover a conexão do "
                    "My Notebook com o Google Drive?"
                ),
                QMessageBox.Yes
                | QMessageBox.No,
                QMessageBox.No,
            )

            if resposta != QMessageBox.Yes:
                return

            self.auth_service.desconectar()
            self._atualizar_estado()
            return

        try:
            self.auth_service.autenticar()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro ao conectar",
                (
                    "Não foi possível conectar ao "
                    "Google Drive.\n\n"
                    f"Detalhes: {error}"
                ),
            )
            return

        self._atualizar_estado()

        QMessageBox.information(
            self,
            "Google Drive conectado",
            (
                "O My Notebook foi conectado "
                "ao Google Drive com sucesso."
            ),
        )

    def _backup_ainda_nao_integrado(
        self,
    ) -> None:
        QMessageBox.information(
            self,
            "Backup do Google Drive",
            (
                "A conexão está funcionando.\n\n"
                "Agora falta ligar esta tela ao banco "
                "do usuário atualmente conectado."
            ),
        )

    def _restauracao_ainda_nao_integrada(
        self,
    ) -> None:
        QMessageBox.information(
            self,
            "Restauração do Google Drive",
            (
                "A conexão está funcionando.\n\n"
                "A restauração será ligada depois "
                "que o usuário atual for repassado "
                "para a janela principal."
            ),
        )


class SettingsHome(QWidget):
    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("SettingsHome")

        self._criar_interface()

    def _criar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            34,
            30,
            34,
            30,
        )
        layout.setSpacing(20)

        title = QLabel("Configurações")
        title.setObjectName("ScreenTitle")

        subtitle = QLabel(
            "Gerencie integrações, backups "
            "e preferências do My Notebook."
        )
        subtitle.setObjectName(
            "ScreenSubtitle"
        )

        drive_section = (
            GoogleDriveSettingsSection()
        )

        future_section = SettingsSection(
            title="Outras configurações",
            description=(
                "Novas preferências do aplicativo "
                "serão organizadas nesta área."
            ),
        )

        future_section.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        future_label = QLabel(
            "Nenhuma configuração adicional "
            "disponível no momento."
        )
        future_label.setObjectName(
            "SettingsInfoLabel"
        )

        future_section.main_layout.addWidget(
            future_label
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(drive_section)
        layout.addWidget(future_section)
        layout.addStretch()