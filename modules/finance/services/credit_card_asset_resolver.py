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
    "nubank_roxinho": CreditCardAssetPreset(
        key="nubank_roxinho",
        label="Nubank Roxinho",
        issuer="nubank.png",
        brand="mastercard.png",
        background_color="#820AD1",
        background=None,
        overlay="glass_reflection.png",
    ),
    "nubank_ultravioleta": CreditCardAssetPreset(
        key="nubank_ultravioleta",
        label="Nubank Ultravioleta",
        issuer="nubank.png",
        brand="mastercard.png",
        background_color="#820AD1",
        background=None,
        overlay="glass_reflection.png",
    ),
    "generic_black": CreditCardAssetPreset(
        key="generic_black",
        label="Genérico Black",
        issuer="skyline.png",
        brand="wild_card.png",
        background_color="#000000",
        background=None,
        overlay="glass_reflection.png",
    ),
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