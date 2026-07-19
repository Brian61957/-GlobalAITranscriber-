from brain.brain_state import BrainState


class WorkingMemory:

    def __init__(self):

        self.state = BrainState()

        self.project = {}

        self.instructions = {}

        self.clip = {}

        self.transcript = ""

        self.thoughts = []

    def remember_project(self, project):

        self.project = project

    def remember_instructions(self, instructions):

        self.instructions = instructions

    def remember_clip(self, clip):

        self.clip = clip

    def remember_transcript(self, transcript):

        self.transcript = transcript

    def think(self, thought):

        self.thoughts.append(thought)

    def latest_thought(self):

        if not self.thoughts:
            return None

        return self.thoughts[-1]