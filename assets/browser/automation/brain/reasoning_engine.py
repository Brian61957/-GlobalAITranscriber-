from automation.brain.rule_engine import RuleEngine
from automation.brain.memory import BrainMemory


class ReasoningEngine:

    def __init__(self):

        self.memory = BrainMemory()
        self.rules = RuleEngine()

    def analyze(self, project):

        text = project["text"]

        parsed_rules = self.rules.parse(text)

        self.memory.remember("project", project)

        self.memory.remember("rules", parsed_rules)

        reasoning = []

        if parsed_rules["ignore_fillers"]:
            reasoning.append(
                "Ignore filler words."
            )

        if parsed_rules["british_spelling"]:
            reasoning.append(
                "Use British spelling."
            )

        if parsed_rules["timestamps"]:
            reasoning.append(
                "Insert timestamps."
            )

        if parsed_rules["multiple_speakers"]:
            reasoning.append(
                "Detect speaker changes."
            )

        if parsed_rules["translate"]:
            reasoning.append(
                "Translate transcript."
            )

        return {

            "rules": parsed_rules,

            "reasoning": reasoning

        }