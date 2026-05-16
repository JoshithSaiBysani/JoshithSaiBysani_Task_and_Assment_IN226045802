from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BUNDLED_PYTHON = Path(
    r"C:\Users\Joshith\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)


def _ensure_supported_python() -> None:
    if sys.version_info[:2] == (3, 12):
        return
    bundled_hint = str(BUNDLED_PYTHON)
    message = (
        "This project must be run with the bundled Python 3.12 runtime.\n\n"
        f"You are currently using: {sys.executable}\n"
        f"Detected version: Python {sys.version.split()[0]}\n\n"
        "Run one of these commands from the project root:\n"
        f'  {bundled_hint} main.py ingest data\\knowledge_base\\customer_support_handbook.pdf\n'
        f'  {bundled_hint} main.py ask \"How long do refunds take after a returned item is received?\"\n'
        f"  {bundled_hint} main.py chat --auto-hitl\n"
    )
    raise SystemExit(message)


_ensure_supported_python()

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rag_support.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
