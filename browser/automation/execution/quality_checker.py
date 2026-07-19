class QualityChecker:

    def check(self, result):

        warnings = []

        transcript = result["formatted"]

        if len(transcript.strip()) == 0:

            warnings.append(
                "Transcript is empty."
            )

        if result["confidence"]["confidence"] < 80:

            warnings.append(
                "Low confidence transcription."
            )

        return {

            "passed": len(warnings) == 0,

            "warnings": warnings

        }