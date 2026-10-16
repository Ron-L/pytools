"""
keepopen — run a script's main() so its window doesn't vanish before you can read it.

A script started by double-click, a Startup shortcut or the Windows search bar gets a console window of its own,
and Windows closes that window the instant the script exits — so an error message (or a result) flashes and is
gone. run() keeps the window open ("Press Enter to close") in exactly those cases, and never otherwise:

  * inside an existing cmd / terminal window  -> no pause (that window stays open anyway)
  * started by another program                -> no pause (a pause would hang the caller)
  * Ctrl+C                                    -> quiet exit, no pause (you asked it to stop)

Usage (see README.md for the copy-paste version with the submodule guard):

    from pytools.keepopen import run

    def main():
        ...

    run(main)                    # pause only when it fails
    run(main, pause="always")    # also pause after success — for scripts whose job is to SHOW something

Ron's pattern, 2026-10-15 (first in ReaderWrangler/serve.py); made shared 2026-10-16.
"""
import os
import sys
import traceback

__all__ = ["run", "owns_its_window"]


def owns_its_window():
    """True when this process has a console window all to itself (double-click / shortcut / search bar).

    Windows reports how many processes share the console: just this script (+ the py launcher) = its own window.
    0 means no console at all (run by another tool) — never treated as owning one. Always False off Windows,
    where scripts are normally run from a terminal that stays open."""
    if os.name != "nt":
        return False
    try:
        import ctypes
        n = ctypes.windll.kernel32.GetConsoleProcessList((ctypes.c_uint * 8)(), 8)
        return 0 < n <= 2
    except Exception:
        return False


def _hold_window():
    try:
        input("\nPress Enter to close this window.")
    except (EOFError, KeyboardInterrupt):
        pass


def run(main, pause="error"):
    """Call main(); keep an own window open on failure (pause="error", the default) or always (pause="always").

    A failure is an uncaught exception (its traceback is printed) or sys.exit() with a message / non-zero code.
    The exit code is preserved, so callers and terminals still see success or failure."""
    if pause not in ("error", "always"):
        raise ValueError('pause must be "error" or "always"')
    code = 0
    try:
        result = main()
        if isinstance(result, int):
            code = result
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(130)
    except SystemExit as e:
        if e.code is None or e.code == 0:
            code = 0
        elif isinstance(e.code, int):
            code = e.code
        else:                                   # sys.exit("message")
            print(e.code, file=sys.stderr)
            code = 1
    except Exception:
        traceback.print_exc()
        code = 1
    if owns_its_window() and (code != 0 or pause == "always"):
        _hold_window()
    sys.exit(code)
