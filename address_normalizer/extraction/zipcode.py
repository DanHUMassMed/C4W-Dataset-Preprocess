import re

from .context import ExtractionContext

WORCESTER_COUNTY_ZIPS = [
    "01005",
    "01031",
    "01037",
    "01068",
    "01074",
    "01083",
    "01092",
    "01094",
    "01331",
    "01366",
    "01368",
    "01420",
    "01430",
    "01434",
    "01436",
    "01438",
    "01440",
    "01441",
    "01451",
    "01452",
    "01453",
    "01462",
    "01467",
    "01468",
    "01473",
    "01475",
    "01501",
    "01503",
    "01504",
    "01505",
    "01506",
    "01507",
    "01508",
    "01509",
    "01510",
    "01515",
    "01516",
    "01518",
    "01519",
    "01520",
    "01522",
    "01523",
    "01524",
    "01525",
    "01526",
    "01527",
    "01529",
    "01531",
    "01532",
    "01534",
    "01535",
    "01536",
    "01537",
    "01538",
    "01540",
    "01541",
    "01542",
    "01543",
    "01545",
    "01546",
    "01550",
    "01560",
    "01561",
    "01562",
    "01564",
    "01566",
    "01568",
    "01569",
    "01570",
    "01571",
    "01581",
    "01583",
    "01585",
    "01586",
    "01588",
    "01590",
    "01601",
    "01602",
    "01603",
    "01604",
    "01605",
    "01606",
    "01607",
    "01608",
    "01609",
    "01610",
    "01611",
    "01612",
    "01613",
    "01614",
    "01615",
    "01653",
    "01655",
    "01740",
    "01745",
    "01747",
    "01756",
    "01757",
    "01772",
    "00000",
]


class ZipCodeExtractor:
    """
    Extracts Zip Code from the end of the address line.
    Priority: 10 (First from end)
    Only accepts ZIPs that belong to Worcester County.
    Does NOT extract if preceded by:
        UNIT, SUITE, STE, or bare #
    """

    priority = 10

    def __init__(self):
        # Match 5-digit ZIP, optionally +4
        self.pattern = re.compile(r"(?P<zip>\d{5}(?:-\d{4})?)$", re.IGNORECASE)

        # Keywords or bare hash that indicate unit, not ZIP
        self.unit_prefix_pattern = re.compile(
            r"((UNIT|SUITE|STE)\s*(#\s*)?|#\s*)$", re.IGNORECASE
        )

        # Worcester County ZIP codes
        self.valid_zips = set(WORCESTER_COUNTY_ZIPS)

    def run(self, ctx: ExtractionContext) -> None:
        if not ctx.address_line:
            return

        addr = ctx.address_line.strip()
        match = self.pattern.search(addr)

        if match:
            start_pos = match.start()
            prefix_context = addr[max(0, start_pos - 10) : start_pos].upper()

            # Skip extraction if preceded by UNIT/SUITE/STE or bare #
            if self.unit_prefix_pattern.search(prefix_context):
                return

            zip_code = match.group("zip").strip()

            # Only keep ZIPs that belong to Worcester County
            if zip_code[:5] in self.valid_zips:
                ctx.data["zip_code"] = zip_code
                ctx.address_line = addr[: match.start()].strip()
