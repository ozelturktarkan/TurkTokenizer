@echo off
setlocal
if not defined TURKTOKENIZER_PYTHON set "TURKTOKENIZER_PYTHON=python"
"%TURKTOKENIZER_PYTHON%" "%~dp0tools\predict_example.py" %*
exit /b %errorlevel%
