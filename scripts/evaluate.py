#!/usr/bin/env python3
"""Run the reference evaluator from a source checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vp_research_core.evaluate import main


if __name__ == "__main__":
    main()

