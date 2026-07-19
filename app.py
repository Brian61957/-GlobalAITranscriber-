import multiprocessing
import os
import subprocess
import sys

import streamlit as st

from ui.theme import apply_theme
from ui.topbar import render_topbar
from ui.auth_page import render_auth_page
from ui.workflow_ui import render_workflow

# Required on Windows when using multiprocessing with the "spawn"
# method (the default on Windows). Without this, child processes
# launched by BrowserProcess will try to re-run the Streamlit app
# instead of the worker function.
if __name__ == "__main__":
    multiprocessing.freeze_support()

# On Streamlit Community Cloud, secrets are set in the app's "Secrets"
# panel (not via a committed .env file) and are exposed through
# st.secrets. The rest of this codebase reads config with os.getenv(),
# so mirror any secrets into the process environment here, once, at
# startup. Locally this is a no-op if you're using a .env file instead.
try:
    for _key, _value in st.secrets.items():
        os.environ.setdefault(_key, str(_value))
except Exception:
    # No secrets.toml present (e.g. running locally with just a .env file)
    pass


@st.cache_resource
def _ensure_playwright_browser_installed():
    """
    Streamlit Community Cloud has no shell post-install hook, so we
    install the Playwright Chromium binary the first time the app boots
    in a fresh container. st.cache_resource makes this run once per
    container lifetime instead of on every rerun.
    """
    marker = "/tmp/.playwright_chromium_installed"
    if os.path.exists(marker):
        return
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )
        with open(marker, "w") as f:
            f.write("done")
    except Exception as e:
        st.warning(f"Playwright browser install step failed: {e}")


_ensure_playwright_browser_installed()

st.set_page_config(
    page_title="Global AI Transcriber",
    page_icon="🌍",
    layout="centered",
)

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "stage" not in st.session_state:
    st.session_state.stage = "idle"

apply_theme()

if not st.session_state.logged_in:
    render_auth_page()
else:
    render_topbar()
    render_workflow()
