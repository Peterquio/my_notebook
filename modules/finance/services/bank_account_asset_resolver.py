from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BankAccountAssetPreset:
    key: str
    label: str
    institution: str
    background_color: str
    text_color: str = "#FFFFFF"
    logo: str | None = None
    background: str | None = None
    overlay: str | None = None


@dataclass(frozen=True)
class BankAccountResolvedAssets:
    key: str
    label: str
    institution: str
    background_color: str
    text_color: str
    logo_path: Path | None = None
    background_path: Path | None = None
    overlay_path: Path | None = None


BANK_ACCOUNT_ASSET_PRESETS: dict[str, BankAccountAssetPreset] = {
    "nubank": BankAccountAssetPreset(
        key="nubank",
        label="Nubank",
        institution="Nubank",
        logo="nubank.png",
        background_color="#6D28D9",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "inter": BankAccountAssetPreset(
        key="inter",
        label="Inter",
        institution="Banco Inter",
        logo="inter.png",
        background_color="#F97316",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "itau": BankAccountAssetPreset(
        key="itau",
        label="Itaú",
        institution="Itaú",
        logo="itau.png",
        background_color="#EA580C",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "bradesco": BankAccountAssetPreset(
        key="bradesco",
        label="Bradesco",
        institution="Bradesco",
        logo="bradesco.png",
        background_color="#B91C1C",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "santander": BankAccountAssetPreset(
        key="santander",
        label="Santander",
        institution="Santander",
        logo="santander.png",
        background_color="#DC2626",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "bb": BankAccountAssetPreset(
        key="bb",
        label="Banco do Brasil",
        institution="Banco do Brasil",
        logo="bb.png",
        background_color="#FACC15",
        text_color="#1E3A8A",
        overlay="glass_reflection.png",
    ),
    "caixa": BankAccountAssetPreset(
        key="caixa",
        label="Caixa",
        institution="Caixa",
        logo="caixa.png",
        background_color="#2563EB",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "btg": BankAccountAssetPreset(
        key="btg",
        label="BTG",
        institution="BTG Pactual",
        logo="btg.png",
        background_color="#020617",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "xp": BankAccountAssetPreset(
        key="xp",
        label="XP",
        institution="XP",
        logo="xp.png",
        background_color="#111827",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "picpay": BankAccountAssetPreset(
        key="picpay",
        label="PicPay",
        institution="PicPay",
        logo="picpay.png",
        background_color="#16A34A",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "pagbank": BankAccountAssetPreset(
        key="pagbank",
        label="PagBank",
        institution="PagBank",
        logo="pagbank.png",
        background_color="#FACC15",
        text_color="#111827",
        overlay="glass_reflection.png",
    ),
    "mercado_pago": BankAccountAssetPreset(
        key="mercado_pago",
        label="Mercado Pago",
        institution="Mercado Pago",
        logo="mercado_pago.png",
        background_color="#38BDF8",
        text_color="#0F172A",
        overlay="glass_reflection.png",
    ),
    "will_bank": BankAccountAssetPreset(
        key="will_bank",
        label="Will Bank",
        institution="Will Bank",
        logo="will_bank.png",
        background_color="#FACC15",
        text_color="#111827",
        overlay="glass_reflection.png",
    ),
    "neon": BankAccountAssetPreset(
        key="neon",
        label="Neon",
        institution="Neon",
        logo="neon.png",
        background_color="#00BFFF",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "sicoob": BankAccountAssetPreset(
        key="sicoob",
        label="Sicoob",
        institution="Sicoob",
        logo="sicoob.png",
        background_color="#064E3B",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "sicredi": BankAccountAssetPreset(
        key="sicredi",
        label="Sicredi",
        institution="Sicredi",
        logo="sicredi.png",
        background_color="#065F46",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
    "generic_bank": BankAccountAssetPreset(
        key="generic_bank",
        label="Conta Bancária",
        institution="Banco",
        logo=None,
        background_color="#334155",
        text_color="#FFFFFF",
        overlay="glass_reflection.png",
    ),
}


class BankAccountAssetResolver:
    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[3]
        self.banks_assets_dir = self.project_root / "assets" / "banks"

    def listar_presets(self) -> list[BankAccountAssetPreset]:
        return list(BANK_ACCOUNT_ASSET_PRESETS.values())

    def obter_preset(self, key: str) -> BankAccountAssetPreset | None:
        return BANK_ACCOUNT_ASSET_PRESETS.get(key)

    def resolver_preset(self, key: str | None) -> BankAccountResolvedAssets:
        if not key:
            key = "generic_bank"

        preset = self.obter_preset(key)

        if preset is None:
            preset = BANK_ACCOUNT_ASSET_PRESETS["generic_bank"]

        logo_path = None
        if preset.logo:
            logo_path = self.banks_assets_dir / "logos" / preset.logo
            if not logo_path.exists():
                logo_path = None

        background_path = None
        if preset.background:
            background_path = self.banks_assets_dir / "backgrounds" / preset.background
            if not background_path.exists():
                background_path = None

        overlay_path = None
        if preset.overlay:
            overlay_path = self.banks_assets_dir / "overlays" / preset.overlay
            if not overlay_path.exists():
                overlay_path = None

        return BankAccountResolvedAssets(
            key=preset.key,
            label=preset.label,
            institution=preset.institution,
            background_color=preset.background_color,
            text_color=preset.text_color,
            logo_path=logo_path,
            background_path=background_path,
            overlay_path=overlay_path,
        )