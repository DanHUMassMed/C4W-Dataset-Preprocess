from typing import Protocol, runtime_checkable

from .context import ExtractionContext


@runtime_checkable
class Extractor(Protocol):
    priority: int

    def run(self, ctx: ExtractionContext) -> None:
        """Mutates ctx in place. Never raises for missing data."""
        ...
