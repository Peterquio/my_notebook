from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CreditCardAssetPreset:
    key: str
    label: str
    issuer: str
    brand: str
    background_color: str
    text_color: str = "#FFFFFF"
    background: str | None = None
    overlay: str | None = None
    chip: str = "chip.png"


@dataclass(frozen=True)
class CreditCardResolvedAssets:
    key: str
    label: str
    background_color: str
    text_color: str
    issuer_path: Path
    brand_path: Path
    chip_path: Path
    background_path: Path | None = None
    overlay_path: Path | None = None


CARD_ASSET_PRESETS: dict[str, CreditCardAssetPreset] = {
    "nubank_gold": CreditCardAssetPreset("nubank_gold", "Nubank Gold", "nubank.png", "mastercard.png", "#7C3AED", "#FFFFFF", None, "glass_reflection.png"),
    "nubank_platinum": CreditCardAssetPreset("nubank_platinum", "Nubank Platinum", "nubank.png", "mastercard.png", "#6D28D9", "#FFFFFF", None, "glass_reflection.png"),
    "nubank_ultravioleta": CreditCardAssetPreset("nubank_ultravioleta", "Nubank Ultravioleta", "nubank.png", "mastercard.png", "#111111", "#FFFFFF", None, "glass_reflection.png"),

    "inter_gold": CreditCardAssetPreset("inter_gold", "Inter Gold", "skyline.png", "mastercard.png", "#F97316", "#FFFFFF", None, "glass_reflection.png"),
    "inter_platinum": CreditCardAssetPreset("inter_platinum", "Inter Platinum", "skyline.png", "mastercard.png", "#CBD5E1", "#111827", None, "glass_reflection.png"),
    "inter_black": CreditCardAssetPreset("inter_black", "Inter Black", "skyline.png", "mastercard.png", "#050505", "#FFFFFF", None, "glass_reflection.png"),

    "c6_standard": CreditCardAssetPreset("c6_standard", "C6", "c6.png", "mastercard.png", "#111827", "#FFFFFF", None, "glass_reflection.png"),
    "c6_platinum": CreditCardAssetPreset("c6_platinum", "C6 Platinum", "c6.png", "mastercard.png", "#94A3B8", "#111827", None, "glass_reflection.png"),
    "c6_carbon": CreditCardAssetPreset("c6_carbon", "C6 Carbon", "c6.png", "mastercard.png", "#020617", "#FFFFFF", None, "glass_reflection.png"),

    "bb_ourocard_facil": CreditCardAssetPreset("bb_ourocard_facil", "Ourocard Fácil", "bb.png", "visa.png", "#FACC15", "#1E3A8A", None, "glass_reflection.png"),
    "bb_ourocard_platinum": CreditCardAssetPreset("bb_ourocard_platinum", "Ourocard Platinum", "bb_silver.png", "visa.png", "#CBD5E1", "#1E3A8A", None, "glass_reflection.png"),
    "bb_altus": CreditCardAssetPreset("bb_altus", "Altus", "bb_gold.png", "visa.png", "#111827", "#FACC15", None, "glass_reflection.png"),

    "itau_click": CreditCardAssetPreset("itau_click", "Click", "itau.png", "visa.png", "#F97316", "#FFFFFF", None, "glass_reflection.png"),
    "itau_pao_de_acucar": CreditCardAssetPreset("itau_pao_de_acucar", "Pão de Açúcar", "itau_az.png", "mastercard.png", "#14532D", "#FFFFFF", None, "glass_reflection.png"),
    "itau_personnalite_black": CreditCardAssetPreset("itau_personnalite_black", "Personnalité Black", "itau_bco.png", "mastercard.png", "#050505", "#FFFFFF", None, "glass_reflection.png"),

    "bradesco_neo": CreditCardAssetPreset("bradesco_neo", "Neo", "bradesco.png", "visa.png", "#B91C1C", "#FFFFFF", None, "glass_reflection.png"),
    "bradesco_elo_nanquim": CreditCardAssetPreset("bradesco_elo_nanquim", "Elo Nanquim", "bradesco_bco.png", "elo.png", "#030712", "#FFFFFF", None, "glass_reflection.png"),
    "bradesco_aeternum": CreditCardAssetPreset("bradesco_aeternum", "Aeternum", "bradesco_bco.png", "visa.png", "#111827", "#E5E7EB", None, "glass_reflection.png"),

    "santander_sx": CreditCardAssetPreset("santander_sx", "SX", "santander.png", "visa.png", "#DC2626", "#FFFFFF", None, "glass_reflection.png"),
    "santander_unique": CreditCardAssetPreset("santander_unique", "Unique", "santander_bco.png", "mastercard.png", "#050505", "#FFFFFF", None, "glass_reflection.png"),
    "santander_unlimited": CreditCardAssetPreset("santander_unlimited", "Unlimited", "santander_silver.png", "visa.png", "#111827", "#E5E7EB", None, "glass_reflection.png"),

    "caixa_sim": CreditCardAssetPreset("caixa_sim", "SIM", "caixa.png", "visa.png", "#2563EB", "#FFFFFF", None, "glass_reflection.png"),
    "caixa_elo_grafite": CreditCardAssetPreset("caixa_elo_grafite", "Elo Grafite", "caixa.png", "elo.png", "#374151", "#FFFFFF", None, "glass_reflection.png"),

    "btg_black": CreditCardAssetPreset("btg_black", "BTG Black", "btg.png", "mastercard.png", "#020617", "#FFFFFF", None, "glass_reflection.png"),
    "xp_visa_infinite": CreditCardAssetPreset("xp_visa_infinite", "XP Visa Infinite", "xp.png", "visa.png", "#111827", "#FFFFFF", None, "glass_reflection.png"),
    "picpay_card": CreditCardAssetPreset("picpay_card", "PicPay Card", "picpay.png", "mastercard.png", "#16A34A", "#FFFFFF", None, "glass_reflection.png"),
    "pagbank_visa": CreditCardAssetPreset("pagbank_visa", "PagBank Visa", "pagbank.png", "visa.png", "#FACC15", "#111827", None, "glass_reflection.png"),
    "mercado_pago_visa": CreditCardAssetPreset("mercado_pago_visa", "Mercado Pago Visa", "mercado_pago.png", "visa.png", "#38BDF8", "#0F172A", None, "glass_reflection.png"),
    "will_bank": CreditCardAssetPreset("will_bank", "Will", "will_bank.png", "mastercard.png", "#FACC15", "#111827", None, "glass_reflection.png"),
    "neon_visa": CreditCardAssetPreset("neon_visa", "Neon", "neon.png", "visa.png", "#00BFFF", "#FFFFFF", None, "glass_reflection.png"),
    "sicoob_merit": CreditCardAssetPreset("sicoob_merit", "Merit", "sicoob.png", "mastercard.png", "#064E3B", "#FFFFFF", None, "glass_reflection.png"),
    "sicredi_visa_infinite": CreditCardAssetPreset("sicredi_visa_infinite", "Visa Infinite", "Sicredi-logo.png", "visa.png", "#065F46", "#FFFFFF", None, "glass_reflection.png"),

    "generic_black": CreditCardAssetPreset("generic_black", "Cartão Genérico", "skyline.png", "wild_card.png", "#000000", "#FFFFFF", None, "glass_reflection.png"),
}


class CreditCardAssetResolver:
    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[3]
        self.cards_assets_dir = self.project_root / "assets" / "cards"

    def listar_presets(self) -> list[CreditCardAssetPreset]:
        return list(CARD_ASSET_PRESETS.values())

    def obter_preset(self, key: str) -> CreditCardAssetPreset | None:
        return CARD_ASSET_PRESETS.get(key)

    def resolver_preset(self, key: str) -> CreditCardResolvedAssets:
        preset = self.obter_preset(key)

        if preset is None:
            raise ValueError(f"Preset de cartão não encontrado: {key}")

        issuer_path = self.cards_assets_dir / "issuers" / preset.issuer
        brand_path = self.cards_assets_dir / "brands" / preset.brand
        background_path = None
        if preset.background:
            background_path = self.cards_assets_dir / "backgrounds" / preset.background
            if not background_path.exists():
                background_path = None
        chip_path = self.cards_assets_dir / preset.chip

        overlay_path = None
        if preset.overlay:
            overlay_path = self.cards_assets_dir / "overlays" / preset.overlay

        self._validar_arquivo_obrigatorio(issuer_path, "issuer")
        self._validar_arquivo_obrigatorio(brand_path, "brand")
        if background_path is not None:
            self._validar_arquivo_obrigatorio(background_path, "background")
        self._validar_arquivo_obrigatorio(chip_path, "chip")

        if overlay_path is not None and not overlay_path.exists():
            overlay_path = None

        return CreditCardResolvedAssets(
            key=preset.key,
            label=preset.label,
            background_color=preset.background_color,
            text_color=preset.text_color,
            issuer_path=issuer_path,
            brand_path=brand_path,
            background_path=background_path,
            chip_path=chip_path,
            overlay_path=overlay_path,
        )

    def _validar_arquivo_obrigatorio(self, path: Path, asset_type: str) -> None:
        if not path.exists():
            raise FileNotFoundError(
                f"Asset obrigatório não encontrado para '{asset_type}': {path}"
            )