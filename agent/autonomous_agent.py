from agent.agent_context import AgentContext
from agent.agent_state import AgentState
from agent.cycle_result import CycleResult


class AutonomousAgent:

    def __init__(self, executor):

        self.context = AgentContext()

        self.executor = executor

        # Runtime state (NOT BrainState)
        self.state = AgentState()

    def initialize(self, project, clip):

        self.context.project = project

        self.context.clip = clip

        # Initialize the Brain
        self.context.brain.initialize(
            project,
            clip
        )

        # Initialize Agent runtime state
        self.state.running = True
        self.state.paused = False
        self.state.stopped = False

        self.state.current_cycle = 0
        self.state.current_action = ""

        self.state.completed_actions = 0
        self.state.failed_actions = 0

        self.state.last_result = ""

        self.state.status = "Running"

    def cycle(self):

        # Increment runtime cycle
        self.state.current_cycle += 1

        # Ask Brain what to do next
        decision = self.context.brain.next_action()

        # Execute the decision
        result = self.executor.execute(decision)

        # Save current action
        self.state.current_action = decision.action

        self.state.last_result = result.message

        # Update Brain only if execution succeeded
        if result.success:

            self.context.brain.complete_action(
                decision.action
            )

            self.state.completed_actions += 1

        else:

            self.state.failed_actions += 1

        # Check whether Brain says execution is finished
        finished = decision.completed

        if finished:

            self.state.running = False
            self.state.status = "Completed"

        return CycleResult(

            cycle=self.state.current_cycle,

            action=decision.action,

            success=result.success,

            continue_execution=not finished,

            message=result.message,

            confidence=decision.confidence

        )

    def stop(self):

        self.state.running = False
        self.state.stopped = True
        self.state.status = "Stopped"

    def pause(self):

        self.state.paused = True
        self.state.running = False
        self.state.status = "Paused"

    def resume(self):

        self.state.paused = False
        self.state.running = True
        self.state.status = "Running"