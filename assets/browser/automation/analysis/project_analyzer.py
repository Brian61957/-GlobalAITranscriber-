from automation.analysis.language_detector import LanguageDetector
from automation.analysis.instruction_analyzer import InstructionAnalyzer
from automation.analysis.audio_analyzer import AudioAnalyzer
from automation.analysis.draft_analyzer import DraftAnalyzer


class ProjectAnalyzer:

    def __init__(self):

        self.language = LanguageDetector()

        self.instructions = InstructionAnalyzer()

        self.audio = AudioAnalyzer()

        self.draft = DraftAnalyzer()

    def analyze(self, project):

        return {

            "language": self.language.detect(project),

            "rules": self.instructions.analyze(project),

            "audio": self.audio.analyze(project),

            "draft": self.draft.analyze(project)

        }