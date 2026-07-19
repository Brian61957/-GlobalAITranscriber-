class Planner:

    def build(self, analysis):

        rules = analysis["rules"]

        plan = []

        plan.append("Load Audio")

        plan.append("Speech Recognition")

        if rules["translate"]:

            plan.append("Translation")

        if rules["ignore_fillers"]:

            plan.append("Remove Fillers")

        if rules["multiple_speakers"]:

            plan.append("Speaker Detection")

        if rules["timestamps"]:

            plan.append("Insert Timestamps")

        plan.append("Formatting")

        plan.append("Quality Check")

        plan.append("Export")

        return plan