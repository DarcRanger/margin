@echo off
REM One-command Margin quality gate for Windows Command Prompt.
python "%~dp0scripts\margin_test.py" --full %*
