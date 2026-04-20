from __future__ import annotations

import sys
from pathlib import Path

from streamlit.web.cli import main as streamlit_main


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    sys.argv = ["streamlit", "run", str(project_root / "app" / "main.py")]
    raise SystemExit(streamlit_main())
