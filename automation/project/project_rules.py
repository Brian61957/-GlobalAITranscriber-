class ProjectRules:

    def build(self, profile):

        rules = {

            "language": profile.language,

            "translate": profile.translate,

            "verbatim": profile.verbatim,

            "ignore_fillers": profile.ignore_fillers,

            "speaker_labels": profile.speaker_labels,

            "timestamps": profile.timestamps,

            "british_spelling": profile.british_spelling,

        }

        return rules