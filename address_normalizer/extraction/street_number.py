import re

from .context import ExtractionContext


class StreetNumberExtractor:
    """
    Extracts street number components from the beginning of an address.

    Optimized for clarity and readability over performance.

    Supports:
      - Simple numbers: 12 Main St
      - Extensions: 12A, 12 A, 12-A, 12.A Main St
      - Alphanumeric extensions: 12 2A Main St
      - Ranges: 12-15, 12 - 15, 12- 15, 12 -15 Main St
      - Fractions: 12 1/2, 121/2 Main St

    Produces:
      street_number     -> the base number (always present if match found)
      street_range_to   -> the ending number for ranges (e.g., '15' from '12-15')
      street_extension  -> letter, alphanumeric, or '1/2' fraction
    """

    priority = 30

    def run(self, ctx: ExtractionContext) -> None:
        """
        Main extraction method.

        Parses the street number components in sequential steps:
        1. Extract base street number
        2. Check for range (e.g., -15 in '12-15')
        3. Check for extension (e.g., 'A' in '12A' or '1/2' in '12 1/2')
        """
        if not ctx.address_line:
            return

        addr = ctx.address_line.strip()

        # Step 1: Extract the base street number
        street_number, remaining = self._extract_base_number(addr)

        if not street_number:
            # No street number found
            return

        # Step 2: Check for a range (e.g., '12-15')
        street_range_to, remaining = self._extract_range(remaining)

        # Step 3: Check for an extension (e.g., 'A', '2A', or '1/2')
        street_extension, remaining = self._extract_extension(remaining)

        # Store the extracted components
        ctx.data["street_number"] = street_number

        if street_range_to:
            ctx.data["street_range_to"] = street_range_to

        if street_extension:
            ctx.data["street_extension"] = street_extension

        # Update the address line to remove the parsed street number portion
        ctx.address_line = remaining.strip()

    def _extract_base_number(self, text: str) -> tuple[str, str]:
        """
        Extract the leading numeric street number.

        Examples:
          '12 Main St' -> ('12', ' Main St')
          '123A Main' -> ('123', 'A Main')
          '12-15 Main' -> ('12', '-15 Main')

        Returns:
          (street_number, remaining_text)
        """
        # Match leading digits at the start of the string
        match = re.match(r"^(\d+)", text)

        if not match:
            return ("", text)

        number = match.group(1)
        remaining = text[len(number) :]

        return (number, remaining)

    def _extract_range(self, text: str) -> tuple[str, str]:
        """
        Extract range number if present (e.g., '15' from '-15' or ' - 15').

        A range is identified by a dash (with optional surrounding spaces)
        followed by digits ONLY.

        Examples:
          '-15 Main St' -> ('15', ' Main St')
          ' - 15 Main St' -> ('15', ' Main St')
          '-A Main St' -> ('', '-A Main St')  # Not a range, it's an extension
          'A Main St' -> ('', 'A Main St')

        Returns:
          (range_to_number, remaining_text)
        """
        # Pattern: optional spaces, dash, optional spaces, then digits only
        # The key is that after the dash there must be ONLY digits (not letters)
        match = re.match(r"^\s*-\s*(\d+)(?=\s|$)", text)

        if not match:
            return ("", text)

        range_to = match.group(1)
        remaining = text[match.end() :]

        return (range_to, remaining)

    def _extract_extension(self, text: str) -> tuple[str, str]:
        """
        Extract extension: letter, alphanumeric, or 1/2 fraction.

        Handles various separators: space, dash, dot, or no separator.

        Examples:
          'A Main St' -> ('A', ' Main St')
          ' A Main St' -> ('A', ' Main St')
          '-A Main St' -> ('A', ' Main St')
          '.A Main St' -> ('A', ' Main St')
          ' 2A Main St' -> ('2A', ' Main St')
          ' 1/2 Main St' -> ('1/2', ' Main St')
          '1/2 Main St' -> ('1/2', ' Main St')

        Returns:
          (extension, remaining_text)
        """
        # Try to match an extension with optional separator (space, dash, or dot)

        # Pattern 1: Check for 1/2 fraction (the only fraction we support)
        # Can be with or without leading space/separator: ' 1/2', '1/2', ' 1/2', '-1/2'
        match = re.match(r"^\s*[-.]?\s*(1/2)(?=\s|$)", text)
        if match:
            extension = match.group(1)
            remaining = text[match.end() :]
            return (extension.upper(), remaining)

        # Pattern 2: Check for alphanumeric extension (e.g., '2A')
        # Must start with digit and contain at least one letter
        match = re.match(r"^\s*[-.]?\s*(\d+[A-Z]+)(?=\s|$)", text, re.IGNORECASE)
        if match:
            extension = match.group(1)
            remaining = text[match.end() :]
            return (extension.upper(), remaining)

        # Pattern 3: Check for single letter extension (e.g., 'A')
        match = re.match(r"^\s*[-.]?\s*([A-Z])(?=\s|$)", text, re.IGNORECASE)
        if match:
            extension = match.group(1)
            remaining = text[match.end() :]
            return (extension.upper(), remaining)

        # No extension found
        return ("", text)
