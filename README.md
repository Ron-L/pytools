# pytools

Small shared Python helpers, used by other repos as a **git submodule** so there's one copy, not several drifting ones.

## keepopen — scripts whose window doesn't vanish

A script started by double-click, a Startup shortcut or the Windows search bar gets its own console window, and
Windows closes it the instant the script ends — an error message flashes and is gone. `keepopen.run()` keeps that
window open ("Press Enter to close") **only** when the script owns its window; never inside an existing terminal
(the window stays anyway), never under another program (a pause would hang it), and not after Ctrl+C.

### Copy-paste: a script in a repo that has pytools as a submodule

```python
import sys

try:
    from pytools.keepopen import run
except ImportError:
    print("This script needs the pytools submodule. In the project folder run:\n"
          "    git submodule update --init\n"
          "then start it again.", file=sys.stderr)
    try:
        input("\nPress Enter to close this window.")
    except (EOFError, KeyboardInterrupt):   # no keyboard (run by another tool) — just exit
        pass
    sys.exit(1)


def main():
    ...  # the script


if __name__ == "__main__":
    run(main)                  # pause only when it fails
    # run(main, pause="always")  # also pause after success — for scripts whose job is to SHOW something
```

### Copy-paste: a stand-alone script (not in a repo)

On Ron's PC, `PYTHONPATH` includes `C:\Users\Ron\Projects`, so the same import works anywhere:

```python
from pytools.keepopen import run

def main():
    ...

run(main)
```

### What counts as failure

An uncaught exception (its traceback is printed), or `sys.exit()` with a message or a non-zero code. The exit code is
passed through, so a terminal or a calling program still sees success or failure.

## Adding pytools to a repo

```bash
git submodule add https://github.com/Ron-L/pytools.git pytools
git commit -m "Add pytools submodule"
```

Cloning a repo that uses it: `git clone --recurse-submodules <url>` — or, after a plain clone,
`git submodule update --init`.

Updating a repo to the newest pytools: `git submodule update --remote pytools`, then commit the new pointer.
