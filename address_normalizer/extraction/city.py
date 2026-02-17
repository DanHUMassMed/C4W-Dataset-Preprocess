import re

from .context import ExtractionContext

worcester_county_towns = [
    "Athol",
    "Auburn",
    "Barre",
    "Berlin",
    "Blackstone",
    "Bolton",
    "Boylston",
    "Brookfield",
    "Charlton",
    "Clinton",
    "Douglas",
    "Dudley",
    "East Brookfield",
    "Fitchburg",
    "Gardner",
    "Grafton",
    "Hardwick",
    "Holden",
    "Hopedale",
    "Hubbardston",
    "Leicester",
    "Leominster",
    "Lunenburg",
    "Mendon",
    "Milford",
    "Millbury",
    "Millville",
    "New Braintree",
    "North Brookfield",
    "Northborough",
    "Northbridge",
    "Oakham",
    "Oxford",
    "Paxton",
    "Petersham",
    "Phillipston",
    "Princeton",
    "Royalston",
    "Rutland",
    "Shrewsbury",
    "Southbridge",
    "Spencer",
    "Sterling",
    "Sturbridge",
    "Sutton",
    "Templeton",
    "Upton",
    "Uxbridge",
    "Warren",
    "Webster",
    "West Boylston",
    "West Brookfield",
    "Westminster",
    "Winchendon",
    "Worcester",
]


class CityExtractor:
    """
    Extracts city using a whitelist of Worcester County towns.
    Matches only known town names at the end of the address.
    Priority: 12
    """

    priority = 12

    def __init__(self):
        # Normalize towns to uppercase
        self.towns = sorted(
            [t.upper() for t in worcester_county_towns],
            key=lambda x: len(x),
            reverse=True,  # longest first (e.g., "NORTH BROOKFIELD")
        )

        # Build regex: (TOWN1|TOWN2|TOWN3)$
        escaped = [re.escape(t) for t in self.towns]
        pattern = r"(?P<city>" + "|".join(escaped) + r")$"

        self.pattern = re.compile(pattern, re.IGNORECASE)

    def run(self, ctx: ExtractionContext) -> None:
        if not ctx.address_line:
            return

        text = ctx.address_line.strip()

        match = self.pattern.search(text)
        if not match:
            return

        city = match.group("city")

        # Store normalized city name
        ctx.data["city"] = city.title()

        # Remove city from address
        ctx.address_line = re.sub(
            re.escape(city) + r"$", "", text, flags=re.IGNORECASE
        ).strip()
