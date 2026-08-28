"""Apply minimal Windows compatibility patches to upstream robust taguchi CLI."""

from __future__ import annotations

import sys
from pathlib import Path


INCLUDE_OLD = """#include <unistd.h>
#include <sys/wait.h>"""

INCLUDE_NEW = """#ifndef _WIN32
#include <unistd.h>
#include <sys/wait.h>
#endif"""

RUN_GUARD = """    // Execute each run as a separate process
    printf("Executing %zu experiment runs using '%s'...\\n", count, script);

    for (size_t i = 0; i < count; i++) {"""

RUN_GUARD_NEW = """    // Execute each run as a separate process
    printf("Executing %zu experiment runs using '%s'...\\n", count, script);

#ifdef _WIN32
    fprintf(stderr, "Error: 'run' command is not supported on Windows\\n");
    taguchi_free_runs(runs, count);
    taguchi_free_definition(def);
    return 1;
#else
    for (size_t i = 0; i < count; i++) {"""


RUN_END_OLD = """    }

    // Cleanup
    taguchi_free_runs(runs, count);
    taguchi_free_definition(def);

    printf("All experiment runs completed.\\n");
    return 0;
}"""

RUN_END_NEW = """    }
#endif

    // Cleanup
    taguchi_free_runs(runs, count);
    taguchi_free_definition(def);

    printf("All experiment runs completed.\\n");
    return 0;
}"""


def patch_main(main_path: Path) -> None:
    text = main_path.read_text(encoding="utf-8")
    if INCLUDE_OLD not in text:
        if INCLUDE_NEW in text:
            print(f"already patched includes: {main_path}", flush=True)
        else:
            raise SystemExit(f"missing expected include block in {main_path}")
    else:
        text = text.replace(INCLUDE_OLD, INCLUDE_NEW, 1)

    if RUN_GUARD not in text:
        if RUN_GUARD_NEW in text:
            print(f"already patched run guard: {main_path}", flush=True)
        else:
            raise SystemExit(f"missing expected run loop block in {main_path}")
    else:
        text = text.replace(RUN_GUARD, RUN_GUARD_NEW, 1)

    if RUN_END_OLD not in text:
        if "#endif\n    \n    // Cleanup" in text:
            print(f"already patched run end: {main_path}", flush=True)
        else:
            raise SystemExit(f"missing expected run end block in {main_path}")
    else:
        text = text.replace(RUN_END_OLD, RUN_END_NEW, 1)

    main_path.write_text(text, encoding="utf-8")
    print(f"patched {main_path}", flush=True)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path/to/optimize/taguchi/src/cli/main.c>", file=sys.stderr)
        return 2
    patch_main(Path(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
