@echo off
REM Script pentru instalare automata a librarii
REM Pune acest fisier in acelasi folder cu job_notifier.py

echo.
echo ========================================
echo  JOB NOTIFIER - Instalare Librarii
echo ========================================
echo.

echo [1/2] Instalez requests...
pip install requests

echo.
echo [2/2] Instalez beautifulsoup4...
pip install beautifulsoup4

echo.
echo ========================================
echo  INSTALARE COMPLETA!
echo ========================================
echo.
echo Daca nu sunt erori rosii, totul e ok!
echo Inchide aceasta fereastra.

pause
