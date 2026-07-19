from brain.working_memory import WorkingMemory

from brain.instruction_reasoner import InstructionReasoner
from brain.clip_reasoner import ClipReasoner
from brain.task_planner import TaskPlanner
from brain.decision_engine import DecisionEngine

from brain.page_reasoner import PageReasoner
from brain.action_policy import ActionPolicy


class Brain:

    def __init__(self):

        self.memory = WorkingMemory()

        self.instruction_reasoner = InstructionReasoner()

        self.clip_reasoner = ClipReasoner()

        self.task_planner = TaskPlanner()

        self.page_reasoner = PageReasoner()

        self.action_policy = ActionPolicy()

        self.decision_engine = DecisionEngine()

        self.tasks = []

        self.latest_snapshot = None

        self.current_situation = None

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def initialize(self, project, clip):

        instruction, thought = self.instruction_reasoner.analyze(project)

        self.memory.remember_project(project)

        self.memory.remember_instructions(instruction)

        self.memory.think(thought)

        clip_info, thought = self.clip_reasoner.analyze(clip)

        self.memory.remember_clip(clip_info)

        self.memory.think(thought)

        self.tasks, thought = self.task_planner.create_plan(

            instruction,

            clip_info

        )

        self.memory.think(thought)

        self.memory.state.goal = instruction.task

        self.memory.state.status = "Ready"

        self.memory.state.total_steps = len(self.tasks)

    # =====================================================
    # PERCEPTION
    # =====================================================

    def observe(self, snapshot):

        self.latest_snapshot = snapshot

        self.memory.state.last_page = snapshot.title

        self.current_situation = self.page_reasoner.analyze(
            snapshot
        )

        self.memory.think(

            f"Situation detected: {self.current_situation.type.value}"

        )

    # =====================================================
    # DECISION
    # =====================================================

    def next_action(self):

        #
        # Situation-first reasoning
        #

        if self.current_situation is not None:

            policy_action = self.action_policy.choose(

                self.current_situation

            )

            #
            # Policy decided to override
            #

            if policy_action != "observe":

                decision, thought = self.decision_engine.create_policy_decision(

                    policy_action

                )

                self.memory.think(thought)

                return decision

        #
        # Fall back to task planner
        #

        decision, thought = self.decision_engine.decide(

            self.tasks

        )

        self.memory.think(thought)

        return decision

    # =====================================================
    # EXECUTION FEEDBACK
    # =====================================================

    def action_completed(self, action_name):

        self.complete_action(action_name)

        self.memory.think(

            f"Completed '{action_name}'."

        )

    def action_failed(

        self,

        action_name,

        reason

    ):

        self.memory.think(

            f"Failed '{action_name}': {reason}"

        )

    # =====================================================
    # TASK MANAGEMENT
    # =====================================================

    def complete_action(self, action_name):

        for task in self.tasks:

            if task.name == action_name:

                task.completed = True

                self.memory.state.completed_steps += 1

                self.memory.state.current_step = action_name

                break

    # =====================================================
    # STATE
    # =====================================================

    def state(self):

        return self.memory.state