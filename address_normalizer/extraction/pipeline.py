from typing import Any

from .base import Extractor
from .city import CityExtractor
from .context import ExtractionContext
from .state import StateExtractor
from .street_name import StreetNameTypeExtractor
from .street_number import StreetNumberExtractor
from .unit import UnitExtractor
from .zipcode import ZipCodeExtractor

EXTRACTORS: list[Extractor] = sorted(
    [
        UnitExtractor(),
        StreetNumberExtractor(),
        StreetNameTypeExtractor(),
        CityExtractor(),
        StateExtractor(),
        ZipCodeExtractor(),
    ],
    key=lambda e: e.priority,
)


class AddressPipeline:
    def __init__(self):
        self.extractors = EXTRACTORS

    def run(self, raw_address: str) -> dict[str, Any]:
        raw_address = raw_address.strip()
        ctx = ExtractionContext(address_line=raw_address)

        for extractor in self.extractors:
            extractor.run(ctx)

        return ctx.data
