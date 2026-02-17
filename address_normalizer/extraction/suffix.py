from typing import Final

STREET_SUFFIX_ABBR: Final[dict[str, str]] = {
    # Full names to Abbr
    "ALLEY": "ALY",
    "AVENUE": "AVE",
    "BOULEVARD": "BLVD",
    "CENTER": "CTR",
    "CIRCLE": "CIR",
    "CIRCUIT": "CIRT",
    "COURT": "CT",
    "CRESCENT": "CRES",
    "CROSSWAY": "CWY",
    "DAM": "DM",
    "DRIVE": "DR",
    "DRIVEWAY": "DRWY",
    "EXTENSION": "EXT",
    "GARDEN": "GDN",
    "GARDENS": "GDNS",
    "GREEN": "GRN",
    "HIGHWAY": "HWY",
    "LANE": "LN",
    "MALL": "MALL",
    "PARK": "PARK",
    "PARKWAY": "PKWY",
    "PATH": "PATH",
    "PLACE": "PL",
    "PLAZA": "PLZ",
    "ROAD": "RD",
    "ROW": "ROW",
    "SQUARE": "SQ",
    "STREET": "ST",
    "TERRACE": "TER",
    "VIEW": "VW",
    "WAY": "WAY",
    "WHARF": "WHF",
    # Common variations/typos could be added here
}

# Inverse mapping if needed, or mapping of variations
# For now, we normalize uppercase input against this dict keys.


def normalize_street_suffix(suffix: str) -> str:
    """
    Normalizes a street suffix to its standard abbreviation.
    Returns the original suffix uppercase if no match found.
    """
    clean_suffix = suffix.strip().upper()

    # Check if it's already an abbr in our values
    if clean_suffix in STREET_SUFFIX_ABBR.values():
        return clean_suffix

    return STREET_SUFFIX_ABBR.get(clean_suffix, clean_suffix)
