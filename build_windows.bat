@echo off
REM ================================================================
REM  Build G-École — Windows (.exe)
REM  Résultat : dist\G-Ecole.exe  (double-clic pour lancer)
REM ================================================================

echo ========================================
echo   Build G-École pour Windows
echo ========================================

REM Installer les dépendances
echo [1/3] Installation des dependances...
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

REM Nettoyer
echo [2/3] Nettoyage...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist G-Ecole.spec del G-Ecole.spec

REM Build
echo [3/3] Creation de l'executable...
pyinstaller ^
  --windowed ^
  --onefile ^
  --name "G-Ecole" ^
  --hidden-import "sqlalchemy.dialects.sqlite" ^
  --hidden-import "sqlalchemy.orm.decl_api" ^
  --hidden-import "reportlab.graphics.barcode.code128" ^
  --hidden-import "PIL.Image" ^
  --hidden-import "openpyxl" ^
  main.py

echo.
echo ========================================
echo   Build termine !
echo   Executable : dist\G-Ecole.exe
echo   Double-cliquez sur G-Ecole.exe pour lancer.
echo ========================================
pause
