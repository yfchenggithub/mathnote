#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compatibility wrapper for legacy command name.

Preferred script:
    python scripts/normalize_text_typography.py ...
"""

from __future__ import annotations

from normalize_text_typography import main


if __name__ == "__main__":
    raise SystemExit(main())

