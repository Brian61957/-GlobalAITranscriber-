"""
speaker_labeler.py

Simple gap-based speaker segmentation using Faster-Whisper's segment
timestamps. When the silence between two consecutive segments exceeds a
threshold, it's treated as a speaker change. This is not true diarization
(which would require pyannote.audio + a HuggingFace token), but it's a
practical approximation that works well for most transcription tasks.

Usage:
    segments = model.transcribe(...) -> segments
    labeled = SpeakerLabeler().label(segments)
    text = "\n".join(labeled)
"""

SPEAKER_CHANGE_GAP = 1.5   # seconds of silence → likely speaker change
MIN_SEGMENT_DURATION = 0.3 # ignore extremely short segments


class SpeakerLabeler:

    def label(self, segments, include_timestamps=False):
        """
        Takes a list of Faster-Whisper segment objects and returns a
        list of strings with Speaker N: prefixes where speaker changes
        are detected.
        """
        results = []
        current_speaker = 1
        prev_end = None

        for segment in segments:
            start = getattr(segment, "start", 0)
            end = getattr(segment, "end", start)
            text = (segment.text or "").strip()

            if not text:
                continue

            duration = end - start
            if duration < MIN_SEGMENT_DURATION:
                continue

            # Detect speaker change from silence gap
            if prev_end is not None:
                gap = start - prev_end
                if gap >= SPEAKER_CHANGE_GAP:
                    current_speaker += 1

            # Format the line
            if include_timestamps:
                minutes, seconds = divmod(int(start), 60)
                time_str = f"[{minutes:02d}:{seconds:02d}] "
            else:
                time_str = ""

            results.append(f"Speaker {current_speaker}: {time_str}{text}")
            prev_end = end

        return results
