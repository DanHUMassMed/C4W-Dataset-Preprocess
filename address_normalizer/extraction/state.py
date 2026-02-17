import re

from .context import ExtractionContext


class StateExtractor:
    """
    Extracts State from the end of the address line (after Zip removal).
    Priority: 11
    """

    priority = 11

    def __init__(self):
        # Specific to MA requirement but generalizable
        # Could be expanded to list of states
        self.pattern = re.compile(r"(?P<state>MA|MASSACHUSETTS)$", re.IGNORECASE)

    def run(self, ctx: ExtractionContext) -> None:
        if not ctx.address_line:
            return

        match = self.pattern.search(ctx.address_line)
        if match:
            # Standardization could happen here (e.g. MASSACHUSETTS -> MA)
            state = match.group("state").strip().upper()
            ctx.data["state"] = "MA" if state == "MASSACHUSETTS" else state
            ctx.address_line = ctx.address_line[: match.start()].strip()
