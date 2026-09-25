@echo off
if not exist "%~dp0output" mkdir "%~dp0output"
call "%~dp0RUST.cmd" < "%~dp0examples\native-request.jsonl" > "%~dp0output\native-demo.json"
if errorlevel 1 exit /b 1
echo Output: %~dp0output\native-demo.json
