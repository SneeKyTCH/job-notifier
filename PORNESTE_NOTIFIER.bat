@echo off
chcp 65001 >nul
title Job Notifier - Romania
echo ============================================================
echo  JOB NOTIFIER - Pornit
echo ============================================================
echo.
set PYTHONIOENCODING=utf-8
python "%~dp0job_notifier.py"
echo.
echo Scriptul s-a oprit. Apasa orice tasta pentru a inchide.
pause >nul
