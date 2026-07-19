from automation.brain.reasoning_engine import ReasoningEngine
from automation.brain.planner import Planner


class DecisionEngine:

    def __init__(self):

        self.reasoning = ReasoningEngine()

        self.planner = Planner()

    def decide(self, project):

        analysis = self.reasoning.analyze(project)

        plan = self.planner.build(analysis)

        return {

            "analysis": analysis,

            "plan": plan

        }