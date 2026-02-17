from .context import ExtractionContext
from .suffix import STREET_SUFFIX_ABBR, normalize_street_suffix


class StreetNameTypeExtractor:
    """
    Extracts Street Name and Type from the remainder.
    Priority: 40 (Last)
    """

    priority = 40

    def __init__(self):
        self.suffix_map = STREET_SUFFIX_ABBR
        self.normalize_suffix = normalize_street_suffix

    def run(self, ctx: ExtractionContext) -> None:
        if not ctx.address_line:
            return

        clean_addr = ctx.address_line.upper()
        if not clean_addr:
            return

        parts = clean_addr.rsplit(" ", 1)
        if len(parts) == 2:
            possible_name, possible_type = parts
            norm_type = self.normalize_suffix(possible_type)

            # If it's a known suffix (mapped or already abbr)
            if norm_type != possible_type or possible_type in self.suffix_map.values():
                ctx.data["street_name"] = possible_name
                ctx.data["street_type"] = norm_type
            else:
                # Fallback: treat whole thing as name
                ctx.data["street_name"] = clean_addr
        else:
            ctx.data["street_name"] = clean_addr
