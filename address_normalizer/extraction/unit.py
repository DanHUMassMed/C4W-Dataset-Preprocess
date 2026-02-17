import re

from .context import ExtractionContext


class UnitExtractor:
    """
    Extracts Unit/Suite information from address lines.
    Supports old and new formats, including:
      UNIT #1, APT#1, FLOOR #1, SUITE 401 #118
      APT.3, APT. 1, APT. A, SPACE 1B, UNIT 803-LOFT 1
      1ST FLOOR, 2ND FLOOR, SUITE 404 B, SUITE 284 NORTH
      SUITE #803 LOFT 3
    """

    priority = 20

    def __init__(self):
        # Normalize APT. → APT (allow optional space after dot)
        self.dot_normalizer = re.compile(r"\b([A-Z]+)\.\s*", re.IGNORECASE)

        # Normalize APT#1 → APT #1
        self.hash_normalizer = re.compile(r"([A-Z]+)#", re.IGNORECASE)

        # Normalize ordinals: 1ST → 1 ST
        self.ordinal_normalizer = re.compile(r"(\d+)(ST|ND|RD|TH)\b", re.IGNORECASE)

        # Collapse multiple spaces
        self.space_normalizer = re.compile(r"\s+")

        # Main pattern: DESIGNATOR first
        self.designator_pattern = re.compile(
            r"\b(APT|APARTMENT|STE|SUITE|UNIT|FL|FLOOR|RM|ROOM|DEPT|BLDG|SPACE)\s+(.+)$",
            re.IGNORECASE,
        )

        # Reversed floor pattern: 1ST FLOOR
        self.reverse_floor_pattern = re.compile(
            r"(\d+)\s*(ST|ND|RD|TH)?\s+FLOOR$", re.IGNORECASE
        )

        # Trailing "#123 LOFT 3" pattern
        self.hash_leading_pattern = re.compile(r"#\s*([\w-]+(?:\s+\w+)*)$")

    # ---------------------------

    def _normalize(self, text: str) -> str:
        text = text.upper()
        # Dot after designator → replace with space
        text = self.dot_normalizer.sub(r"\1 ", text)
        # APT#1 → APT #1
        text = self.hash_normalizer.sub(r"\1 #", text)
        # 1ST → 1 ST
        text = self.ordinal_normalizer.sub(r"\1 \2", text)
        # Collapse multiple spaces
        text = self.space_normalizer.sub(" ", text)
        return text.strip()

    # ---------------------------

    def _clean_unit(self, text: str) -> str:
        """Clean up extra spaces and return standardized unit string."""
        text = self.space_normalizer.sub(" ", text)
        return text.strip()

    # ---------------------------

    def run(self, ctx: ExtractionContext) -> None:
        if not ctx.address_line:
            return

        addr = self._normalize(ctx.address_line)

        # 1️⃣ Check reversed floor (1ST FLOOR)
        match = self.reverse_floor_pattern.search(addr)
        if match:
            floor = match.group(1)
            ctx.data["unit"] = f"FLOOR {floor}"
            ctx.address_line = addr[: match.start()].strip()
            return

        # 2️⃣ Check standard designator (APT, UNIT, SUITE, SPACE, etc.)
        match = self.designator_pattern.search(addr)
        if match:
            desig = match.group(1)
            rest = match.group(2).lstrip("#").strip()  # remove leading #
            unit = f"{desig} {rest}"
            ctx.data["unit"] = self._clean_unit(unit)
            ctx.address_line = addr[: match.start()].strip()
            return

        # 3️⃣ Check trailing # pattern (e.g., "#803 LOFT 3")
        match = self.hash_leading_pattern.search(addr)
        if match:
            rest = match.group(1)
            ctx.data["unit"] = f"UNIT {rest}"
            ctx.address_line = addr[: match.start()].strip()
            return

        # 4️⃣ No match → leave address_line as-is
        ctx.address_line = addr
