from core.themes import theme_tokens
from core.themes.card_variants import CARD_VARIANTS

class ThemeManager:
    @property
    def sidebar_bg(self) -> str:
        return theme_tokens.SIDEBAR_BG

    @property
    def sidebar_button_selected(self) -> str:
        return theme_tokens.SIDEBAR_BUTTON_SELECTED

    @property
    def sidebar_button_hover(self) -> str:
        return theme_tokens.SIDEBAR_BUTTON_HOVER

    @property
    def sidebar_button_text(self) -> str:
        return theme_tokens.SIDEBAR_BUTTON_TEXT

    @property
    def sidebar_separator(self) -> str:
        return theme_tokens.SIDEBAR_SEPARATOR

    @property
    def sidebar_button_transparent(self) -> str:
        return theme_tokens.SIDEBAR_BUTTON_TRANSPARENT

    def get_card_variant(self, variant_name: str) -> dict:
        return CARD_VARIANTS.get(
            variant_name,
            CARD_VARIANTS["default"],
        )

theme = ThemeManager()