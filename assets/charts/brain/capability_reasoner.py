from brain.capability import Capability
from brain.situation_type import SituationType


class CapabilityReasoner:

    def determine(self, situation):

        if situation.type == SituationType.LOGIN:
            return Capability.WAIT_FOR_LOGIN

        if situation.type == SituationType.INSTRUCTIONS:
            return Capability.READ_INSTRUCTIONS

        if situation.type == SituationType.TRANSCRIPTION:

            if situation.can_transcribe:
                return Capability.PLAY_AUDIO

            if situation.can_submit:
                return Capability.SUBMIT_TRANSCRIPT

            return Capability.OBSERVE

        if situation.type == SituationType.FINISHED:
            return Capability.FINISHED

        return Capability.OBSERVE