#!/usr/bin/env python3
"""Simple requirements checker: verifies critical packages exist in requirements.txt
Usage: python scripts/check_requirements.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "requirements.txt"

REQUIRED = ["fastapi", "uvicorn", "reportlab"]

if not REQ_FILE.exists():
    print(f"ERROR: requirements.txt not found at {REQ_FILE}")
    sys.exit(2)

lines = [l.strip() for l in REQ_FILE.read_text(encoding='utf-8').splitlines() if l.strip() and not l.strip().startswith('#')]
# Extract package names (before == or >= or ~= or < etc)
pkgs = []
for l in lines:
    # split by common separators
    for sep in ['==','>=','<=','~=','>','<','!=']:
        if sep in l:
            name = l.split(sep,1)[0].strip()
            break
    else:
        name = l.split()[0]
    # handle extras like package[extra]
    name = name.split('[')[0]
    pkgs.append(name.lower())

missing = [p for p in REQUIRED if p.lower() not in pkgs]

print(f"Found {len(pkgs)} packages in requirements.txt")
if missing:
    print("Missing required packages:")
    for m in missing:
        print(f" - {m}")
    print("\nPlease add them to requirements.txt before deploying to Vercel.")
    sys.exit(1)

print("All required packages present: ", ", ".join(REQUIRED))
sys.exit(0)
