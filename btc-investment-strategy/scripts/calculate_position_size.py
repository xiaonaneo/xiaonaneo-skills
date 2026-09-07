#!/usr/bin/env python3
"""Calculate a capped BTC spot position for a validated add candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from risk_model import RiskConfigError, calculate_position_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("risk_config", type=Path)
    parser.add_argument("--signal", required=True)
    parser.add_argument("--price", required=True, type=float)
    args = parser.parse_args()
    try:
        config = json.loads(args.risk_config.read_text(encoding="utf-8"))
        result = calculate_position_size(config, args.signal, args.price)
    except (OSError, json.JSONDecodeError, RiskConfigError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    result["status"] = "ok"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
