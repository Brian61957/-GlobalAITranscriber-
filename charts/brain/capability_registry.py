from brain.capability import Capability


class CapabilityRegistry:

    def __init__(self):

        self.capabilities = {

            Capability.WAIT_FOR_LOGIN,

            Capability.READ_INSTRUCTIONS,

            Capability.PLAY_AUDIO,

            Capability.TRANSCRIBE_AUDIO,

            Capability.FILL_TRANSCRIPT,

            Capability.SUBMIT_TRANSCRIPT,

            Capability.SKIP_CLIP,

            Capability.NEXT_CLIP,

            Capability.OBSERVE,

            Capability.FINISHED

        }

    def supports(self, capability):

        return capability in self.capabilities

    def all(self):

        return list(self.capabilities)