from automation.execution.clip_processor import ClipProcessor
from automation.execution.quality_checker import QualityChecker


class ExecutionPipeline:

    def __init__(self):

        self.processor = ClipProcessor()
        self.quality = QualityChecker()

    def run(self, audio_path):

        result = self.processor.process(audio_path)

        quality = self.quality.check(result)

        return {

            "result": result,

            "quality": quality

        }