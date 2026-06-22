#!/bin/bash
# ================================================================
#  Build G-École — macOS (.app)
#  Résultat : dist/G-Ecole.app  (double-clic pour lancer)
# ================================================================

set -e

echo "========================================"
echo "  Build G-École pour macOS"
echo "========================================"

# Installer les dépendances si besoin
echo "[1/3] Installation des dépendances..."
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

# Nettoyer les builds précédents
echo "[2/3] Nettoyage..."
rm -rf dist/ build/ G-Ecole.spec 2>/dev/null || true

# Build
echo "[3/3] Création du bundle .app..."
pyinstaller \
  --windowed \
  --name "G-Ecole" \
  --hidden-import "sqlalchemy.dialects.sqlite" \
  --hidden-import "sqlalchemy.orm.decl_api" \
  --hidden-import "reportlab.graphics.barcode.code128" \
  --hidden-import "PIL.Image" \
  --hidden-import "openpyxl" \
  main.py

echo ""
echo "========================================"
echo "  ✅  Build terminé !"
echo "  App : dist/G-Ecole.app"
echo "  Double-cliquez sur G-Ecole.app pour lancer."
echo "========================================"
