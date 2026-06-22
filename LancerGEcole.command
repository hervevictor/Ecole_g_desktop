#!/bin/bash
# Lanceur macOS rapide — double-clic pour démarrer G-École
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
python main.py
