from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

import streamlit as st


def _get_executor():
    """
    Playwright's sync API is bound to whichever OS thread created it --
    Streamlit's script runner doesn't guarantee the same thread handles
    every rerun of a session, and when a later rerun (e.g. after you
    click "Confirm & Submit" or "Retry") lands on a different thread
    than the one that opened the browser, Playwright fails with
    "cannot switch to a different thread (which happens to have exited)".

    The fix: route every Playwright-touching call through one
    persistent, single-worker thread pool that lives for the life of
    the browser session, regardless of which thread Streamlit itself
    happens to be running on for any given rerun.
    """
    if "pw_executor" not in st.session_state:
        st.session_state.pw_executor = ThreadPoolExecutor(max_workers=1)
    return st.session_state.pw_executor


def run_in_browser_thread(fn, *args, timeout=120, **kwargs):
    future = _get_executor().submit(fn, *args, **kwargs)

    try:
        return future.result(timeout=timeout)
    except FutureTimeoutError:
        raise RuntimeError(
            f"This step has been running for over {timeout} seconds and may be "
            "stuck (often a Chromium launch issue). Click STOP, then START again. "
            "If it keeps happening, check that Playwright's browser is installed "
            "(`python -m playwright install chromium`)."
        )


def shutdown_browser_thread():
    executor = st.session_state.pop("pw_executor", None)
    if executor:
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            # cancel_futures only exists on Python 3.9+
            executor.shutdown(wait=False)
