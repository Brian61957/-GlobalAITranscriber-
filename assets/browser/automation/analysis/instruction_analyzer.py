from automation.brain.rule_engine import RuleEngine


class InstructionAnalyzer:

    def __init__(self):

        self.rules = RuleEngine()

    def analyze(self, project):

        return self.rules.parse(
            project["text"]
        )