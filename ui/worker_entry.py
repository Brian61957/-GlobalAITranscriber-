"""
worker_entry.py

This module is the FIRST thing imported in the child process.
It kills any asyncio event loop before anything else runs.
Must be imported before any other local module in _worker_main.
"""
import sys
import asyncio


def kill_asyncio():
    """Destroy any existing asyncio event loop unconditionally."""
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()
    except Exception:
        pass

    if sys.platform.startswith("win"):
        try:
            policy = asyncio.WindowsProactorEventLoopPolicy()
            asyncio.set_event_loop_policy(policy)
        except Exception:
            pass

    try:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
    except Exception:
        pass


# Run immediately on import -- before anything else in the child process
kill_asyncio()
