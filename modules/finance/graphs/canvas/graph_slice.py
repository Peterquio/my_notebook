from dataclasses import dataclass, field


@dataclass(slots=True)
class GraphSlice:
    label: str
    value: int
    color: str

    metadata: dict = field(
        default_factory=dict
    )

    selected: bool = False

    @property
    def percentage(self) -> float:
        return float(
            self.metadata.get(
                "percentage",
                0,
            )
        )