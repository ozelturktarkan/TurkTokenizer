@echo off
setlocal
set "TURKTOKENIZER_LOOKUP_INDEX=%~dp0experiments\P111-20260923\data\lookup-index.bin"
"%~dp0bin\turktokenizer.exe" "%~dp0experiments\P81-20260916\data" "%~dp0experiments\P128-20260924\data\frames.json" "%~dp0experiments\P84-20260916\data\bpe.bin"
exit /b %errorlevel%
