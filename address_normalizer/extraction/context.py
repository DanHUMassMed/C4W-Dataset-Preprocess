from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionContext:
    address_line: str
    data: dict[str, Any] = field(default_factory=dict)
    anchors: dict[str, int] = field(default_factory=dict)
