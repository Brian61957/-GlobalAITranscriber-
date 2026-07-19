# Keywords that strongly indicate a candidate is the RIGHT element for a
# given role, checked against its visible text + aria-label. Matching one
# of these adds a big score boost so a specific match like "Start
# Transcribing" reliably wins over an incidental generic button like a
# "Continue" cookie-banner link that also got tagged with the same role.
STRONG_KEYWORDS = {
    "start_button": ["start transcrib", "start recording", "start task", "good luck"],
    "submit_button": ["submit", "save & next", "save and next"],
    "next_button": ["next"],
    "skip_button": ["skip"],
}

# Weaker, more generic fallback keywords for the same roles -- still
# worth a smaller boost, but shouldn't outrank a strong/specific match.
WEAK_KEYWORDS = {
    "start_button": ["start", "begin", "continue", "proceed"],
}


class ActionLocator:

    def _score(self, element, role=None):

        score = 0

        # Prefer visible elements
        if getattr(element, "visible", False):
            score += 50

        # Prefer enabled elements
        if getattr(element, "enabled", False):
            score += 30

        # Prefer elements with text
        if getattr(element, "text", "").strip():
            score += 10

        # Prefer ARIA-labelled elements
        if getattr(element, "aria_label", "").strip():
            score += 5

        # Prefer elements with IDs
        if getattr(element, "element_id", "").strip():
            score += 2

        # Prefer elements whose actual text matches what we're really
        # looking for -- this is what stops an unrelated button that
        # happens to share a role tag from beating the real one.
        if role:
            label = f"{getattr(element, 'text', '')} {getattr(element, 'aria_label', '')}".lower()

            if any(keyword in label for keyword in STRONG_KEYWORDS.get(role, [])):
                score += 100
            elif any(keyword in label for keyword in WEAK_KEYWORDS.get(role, [])):
                score += 20

        return score

    def _collect_candidates(self, snapshot, role):

        candidates = []

        for collection in [

            snapshot.buttons,

            snapshot.textboxes,

            snapshot.dropdowns,

            snapshot.audio_players

        ]:

            for element in collection:

                if element.role == role:

                    candidates.append(element)

        return candidates

    def find(self, snapshot, role):

        candidates = self._collect_candidates(

            snapshot,

            role

        )

        if not candidates:

            return None

        candidates.sort(

            key=lambda element: self._score(element, role),

            reverse=True

        )

        return candidates[0]

    def find_all(self, snapshot, role):

        candidates = self._collect_candidates(

            snapshot,

            role

        )

        candidates.sort(

            key=lambda element: self._score(element, role),

            reverse=True

        )

        return candidates
