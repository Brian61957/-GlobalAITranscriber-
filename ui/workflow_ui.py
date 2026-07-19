import html
from datetime import datetime

import streamlit as st

from automation.pipeline_engine import STATUS_KEYS, NoTasksAvailable
from automation.security.platform_verifier import PlatformVerifier
from utils.url_utils import normalize_url
from speech.provider_factory import PROVIDER_CONFIGS, DEFAULT_MODEL
from ui.topbar import SUPPORT_HTML

MODEL_OPTIONS = list(PROVIDER_CONFIGS.keys())
LANGUAGE_OPTIONS = ["Auto Detect", "English", "French", "Swahili", "Spanish",
                    "Arabic", "Portuguese", "Oromo", "Amharic", "Hausa"]

ICONS = {"pending": "⌛", "running": "⏳", "done": "✓", "error": "✗"}

ACTIVE_STAGES = {
    "processing_initial", "awaiting_review", "processing_next",
    "submitting", "paused", "finished", "no_tasks", "platform_warning",
}


# --------------------------------------------------
# Session state helpers
# --------------------------------------------------

def _init_state():
    defaults = {
        "stage": "idle",
        "status_state": {key: "pending" for key in STATUS_KEYS},
        "log_lines": [],
        "paused": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reset_all():
    proc = st.session_state.pop("browser_proc", None)
    if proc:
        try:
            proc.close()
        except Exception:
            pass
    st.session_state.stage = "idle"
    st.session_state.status_state = {key: "pending" for key in STATUS_KEYS}
    st.session_state.log_lines = []
    st.session_state.paused = False
    for key in ("draft_text", "draft_text_edit", "submit_text",
                "profile_summary", "profile_dos", "profile_donts",
                "error_message", "project_url", "no_tasks_message", "platform_check"):
        st.session_state.pop(key, None)


def _get_proc():
    """Get or create the browser worker thread. Always reuses existing if alive."""
    proc = st.session_state.get("browser_proc")
    if proc is not None and proc.is_alive():
        return proc
    # Old thread is dead or missing -- close cleanly and create fresh
    if proc is not None:
        try:
            proc.close()
        except Exception:
            pass
    from ui.browser_process import BrowserProcess
    new_proc = BrowserProcess()
    st.session_state.browser_proc = new_proc
    return new_proc


def _drain_events(events):
    """Apply events from the worker process into session_state."""
    for ev in events:
        timestamp = datetime.now().strftime("%H:%M:%S")
        if ev.step is not None:
            st.session_state.status_state[ev.step] = ev.status
            line = ev.step + (f" — {ev.detail}" if ev.detail else "")
        else:
            line = ev.detail or ""
        st.session_state.log_lines.append(f"{timestamp} {line}")


# --------------------------------------------------
# Rendering helpers
# --------------------------------------------------

def _render_banner():
    st.markdown('<div class="gat-banner">GLOBAL AI TRANSCRIBER</div>',
                unsafe_allow_html=True)


def _render_controls(running):
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.text_input("Project URL",
                      value=st.session_state.get("project_url", ""),
                      placeholder="Paste any transcription/translation platform URL...",
                      disabled=running, key="project_url_input")
    with col2:
        st.selectbox("Model", MODEL_OPTIONS, disabled=running,
                     key="model_choice_input")
    with col3:
        st.selectbox("Language", LANGUAGE_OPTIONS, disabled=running,
                     key="language_choice_input")


def _render_status_checklist():
    st.markdown('<div class="gat-section-label">Status</div>',
                unsafe_allow_html=True)
    lines = []
    for key in STATUS_KEYS:
        status = st.session_state.status_state.get(key, "pending")
        icon = ICONS.get(status, "⌛")
        lines.append(f'<div class="gat-status-line">{icon} {html.escape(key)}</div>')
    st.markdown("".join(lines), unsafe_allow_html=True)


def _render_log():
    st.markdown('<div class="gat-section-label">Execution Log</div>',
                unsafe_allow_html=True)
    log_text = "\n".join(st.session_state.log_lines[-200:]) or "Waiting to start..."
    st.markdown(f'<div class="gat-log-box">{html.escape(log_text)}</div>',
                unsafe_allow_html=True)


def _render_review_panel():
    engine_task_number = st.session_state.get("task_number", 1)
    summary = st.session_state.get("profile_summary", {})

    with st.expander("📋 Project understanding", expanded=False):
        for key, value in summary.items():
            st.write(f"**{key}**: {value}")
        if st.session_state.get("profile_dos"):
            st.write(f"**dos**: {st.session_state.profile_dos}")
        if st.session_state.get("profile_donts"):
            st.write(f"**donts**: {st.session_state.profile_donts}")

    st.markdown(f"##### ✅ Task {engine_task_number} — Ready to review")
    st.info(
        "The transcript below was typed into the platform automatically. "
        "**Edit it here if it needs corrections**, then click "
        "**✅ Submit & Continue** — the tool will type your edited version "
        "into the platform, click Submit, and load the next clip."
    )
    st.text_area("Transcript (edit before submitting)",
                 value=st.session_state.get("draft_text", ""),
                 height=160, key="draft_text_edit")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Submit & Continue", type="primary",
                     use_container_width=True):
            st.session_state.submit_text = st.session_state.get(
                "draft_text_edit", st.session_state.get("draft_text", ""))
            st.session_state.task_number = engine_task_number + 1
            st.session_state.stage = "submitting"
            st.rerun()
    with col2:
        if st.button("⏹ Stop Here", use_container_width=True):
            proc = st.session_state.get("browser_proc")
            if proc:
                try:
                    proc.close()
                except Exception:
                    pass
            _reset_all()
            st.rerun()


def _render_control_bar():
    running = st.session_state.stage in ACTIVE_STAGES
    col1, col2, col3 = st.columns(3)

    with col1:
        start_disabled = st.session_state.stage not in ("idle",)
        if st.button("▶ START", use_container_width=True,
                     disabled=start_disabled, type="primary"):
            raw_url = st.session_state.get("project_url_input", "").strip()
            try:
                url = normalize_url(raw_url)
            except ValueError as e:
                st.error(str(e))
                url = None

            if url:
                check = PlatformVerifier().verify(url)
                st.session_state.project_url = url
                st.session_state.model_choice = st.session_state.get(
                    "model_choice_input", DEFAULT_MODEL)
                st.session_state.language_choice = st.session_state.get(
                    "language_choice_input", "Auto Detect")
                st.session_state.status_state = {key: "pending" for key in STATUS_KEYS}
                st.session_state.log_lines = []
                st.session_state.task_number = 1

                if check["status"] == "suspicious":
                    st.session_state.platform_check = check
                    st.session_state.stage = "platform_warning"
                else:
                    note = ("Known platform" if check["status"] == "known"
                            else f"Unfamiliar platform, no red flags ({check['domain']})")
                    st.session_state.log_lines.append(
                        f"{datetime.now().strftime('%H:%M:%S')} 🔎 {note}")
                    st.session_state.stage = "processing_initial"

                st.rerun()

    with col2:
        if st.button("⏹ STOP", use_container_width=True):
            proc = st.session_state.get("browser_proc")
            if proc:
                try:
                    proc.close()
                except Exception:
                    pass
            _reset_all()
            st.rerun()

    with col3:
        pause_disabled = st.session_state.stage in ("idle", "finished", "error")
        pause_label = "▶ RESUME" if st.session_state.paused else "⏸ PAUSE"
        if st.button(pause_label, use_container_width=True,
                     disabled=pause_disabled):
            st.session_state.paused = not st.session_state.paused
            if not st.session_state.paused and st.session_state.stage == "paused":
                st.session_state.stage = "processing_next"
            st.rerun()


# --------------------------------------------------
# Main entry point
# --------------------------------------------------

def render_workflow():
    _init_state()

    stage = st.session_state.stage
    running = stage in ACTIVE_STAGES

    st.markdown('<div class="gat-console gat-fade-in">', unsafe_allow_html=True)
    _render_banner()
    _render_controls(running)
    st.markdown('<hr>', unsafe_allow_html=True)
    _render_status_checklist()
    st.markdown('<hr>', unsafe_allow_html=True)
    _render_log()
    st.markdown('<hr>', unsafe_allow_html=True)
    _render_control_bar()
    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # Stage engine
    # --------------------------------------------------

    if stage == "platform_warning":
        check = st.session_state.get("platform_check", {})
        st.warning(
            f"⚠️ **Before continuing:** `{check.get('domain', '?')}` triggered red flags:\n\n"
            + "\n".join(f"- {i}" for i in check.get("issues", []))
            + "\n\nOnly continue if you trust this link."
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚠️ Proceed Anyway", use_container_width=True):
                st.session_state.stage = "processing_initial"
                st.rerun()
        with c2:
            if st.button("Cancel", use_container_width=True, type="primary"):
                _reset_all()
                st.rerun()
        return

    if stage == "processing_initial":
        try:
            proc = _get_proc()
            with st.spinner("Opening platform, reading instructions and transcribing first clip..."):
                profile, events = proc.open_and_understand(
                    st.session_state.project_url,
                    st.session_state.model_choice,
                    st.session_state.language_choice,
                    timeout=600,
                )
                _drain_events(events)
                st.session_state.profile_summary = profile.summary()
                st.session_state.profile_dos = profile.dos
                st.session_state.profile_donts = profile.donts

                transcript, events2 = proc.transcribe()
                _drain_events(events2)

                _, events3 = proc.fill_transcript(transcript)
                _drain_events(events3)

                st.session_state.draft_text = transcript
                st.session_state.stage = "awaiting_review"

        except NoTasksAvailable as e:
            st.session_state.no_tasks_message = str(e)
            st.session_state.stage = "no_tasks"
        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.stage = "error"

        st.rerun()

    elif stage == "processing_next":
        try:
            proc = _get_proc()
            task_num = st.session_state.get("task_number", 2)
            with st.spinner(f"Loading clip {task_num} and transcribing..."):
                transcript, events = proc.transcribe()
                _drain_events(events)

                _, events2 = proc.fill_transcript(transcript)
                _drain_events(events2)

                st.session_state.draft_text = transcript
                st.session_state.stage = "awaiting_review"

        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.stage = "error"

        st.rerun()

    elif stage == "submitting":
        try:
            proc = _get_proc()
            with st.spinner("Submitting transcript and checking for next clip..."):
                text = st.session_state.get("submit_text", "")
                has_next, events = proc.submit(text)
                _drain_events(events)

            if has_next:
                st.session_state.stage = "processing_next"
            else:
                st.session_state.stage = "finished"

        except Exception as e:
            st.session_state.error_message = str(e)
            st.session_state.stage = "error"

        st.rerun()

    elif stage == "awaiting_review":
        _render_review_panel()

    elif stage == "no_tasks":
        st.info(f"📭 {st.session_state.get('no_tasks_message', 'No tasks available right now.')}")
        if st.button("Close Browser & Start New Project", type="primary"):
            _reset_all()
            st.rerun()

    elif stage == "finished":
        st.success("🎉 No more tasks in the queue. Great work!")
        if st.button("Close Browser & Start New Project", type="primary"):
            _reset_all()
            st.rerun()

    elif stage == "error":
        st.error(f"⚠️ {st.session_state.get('error_message', 'Unknown error.')}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔁 Retry", use_container_width=True):
                task_num = st.session_state.get("task_number", 1)
                # Reuse the existing thread/browser -- do NOT create a new
                # BrowserProcess. The existing thread is still alive and
                # Chromium is still open. Creating a new one causes the
                # "Sync API inside asyncio loop" error from overlapping threads.
                st.session_state.stage = (
                    "processing_next" if task_num > 1 else "processing_initial"
                )
                st.rerun()
        with c2:
            if st.button("⏹ Stop", use_container_width=True):
                _reset_all()
                st.rerun()

    # Support footer at the bottom of every workflow page
    st.markdown(SUPPORT_HTML, unsafe_allow_html=True)
