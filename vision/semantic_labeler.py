class SemanticLabeler:

    def _build_description(self, element):

        parts = [

            getattr(element, "text", ""),
            getattr(element, "placeholder", ""),
            getattr(element, "aria_label", ""),
            getattr(element, "title", ""),
            getattr(element, "name", ""),
            getattr(element, "data_testid", ""),
            getattr(element, "classes", ""),
            getattr(element, "element_id", "")

        ]

        return " ".join(str(part) for part in parts if part).lower()

    def _contains(self, description, *keywords):

        return any(keyword in description for keyword in keywords)

    def label(self, snapshot):

        # =====================================================
        # BUTTONS
        # =====================================================

        for button in snapshot.buttons:

            description = self._build_description(button)

            # Submit Transcript
            if self._contains(
                description,
                "submit",
                "finish",
                "complete",
                "save transcript",
                "submit transcript"
            ):

                button.role = "submit_transcript"

            # Skip Clip
            elif self._contains(
                description,
                "skip",
                "next clip"
            ):

                button.role = "skip_clip"

            # Audio Controls
            elif self._contains(
                description,
                "play",
                "listen",
                "recording",
                "audio"
            ):

                button.role = "play_audio"

            elif self._contains(
                description,
                "pause",
                "stop audio"
            ):

                button.role = "pause_audio"

            # Timestamp
            elif self._contains(
                description,
                "timestamp",
                "paste timestamp"
            ):

                button.role = "insert_timestamp"

            # Navigation
            elif self._contains(
                description,
                "next"
            ):

                button.role = "next_clip"

            elif self._contains(
                description,
                "previous",
                "prev",
                "back"
            ):

                button.role = "previous_clip"

            # Speaker Selection Buttons
            elif self._contains(
                description,
                "speaker 1",
                "speaker 2",
                "speaker 3"
            ):

                button.role = "speaker_button"

            # Login
            elif self._contains(
                description,
                "login",
                "sign in",
                "log in"
            ):

                button.role = "login"

            else:

                button.role = "button"

        # =====================================================
        # TEXT EDITORS
        # =====================================================

        for textbox in snapshot.textboxes:

            description = self._build_description(textbox)

            if self._contains(
                description,
                "verbatim",
                "type text",
                "transcript",
                "type here",
                "transcribe"
            ):

                textbox.role = "transcript_editor"

            elif self._contains(
                description,
                "note",
                "comment"
            ):

                textbox.role = "notes"

            else:

                textbox.role = "transcript_editor"

        # =====================================================
        # DROPDOWNS
        # =====================================================

        for dropdown in snapshot.dropdowns:

            description = self._build_description(dropdown)

            if self._contains(
                description,
                "speaker"
            ):

                dropdown.role = "speaker_selector"

            elif self._contains(
                description,
                "tag",
                "language"
            ):

                dropdown.role = "tag_selector"

            elif self._contains(
                description,
                "project"
            ):

                dropdown.role = "project_selector"

            else:

                dropdown.role = "selection"

        # =====================================================
        # AUDIO PLAYERS
        # =====================================================

        for audio in snapshot.audio_players:

            audio.role = "audio_player"

        return snapshot