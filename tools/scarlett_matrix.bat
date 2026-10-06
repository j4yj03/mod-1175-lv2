@echo off
rem Green Stripe 76: automated Scarlett/Dwarf transformer matrix for Windows CMD.
rem Usage (from any directory):
rem   tools\scarlett_matrix.bat devices
rem   tools\scarlett_matrix.bat gainmatch
rem   tools\scarlett_matrix.bat full --repeats 3
rem   tools\scarlett_matrix.bat summary --root test-results\matrix-YYYYMMDD-HHMMSS
rem Device IDs are auto-detected (MME, Focusrite); override with
rem --input-device N --output-device N when the list changes.
setlocal
cd /d "%~dp0.."
python tools\scarlett_matrix.py %*
