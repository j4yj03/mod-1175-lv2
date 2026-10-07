@echo off
setlocal EnableExtensions
rem ============================================================
rem  Green Stripe 76 - REAPER-JSFX-Verknuepfungen
rem
rem  Legt fuer alle Dateien in diesem Ordner (ausser README.md
rem  und diesem Skript) Windows-Symlinks in den REAPER-Ordner:
rem
rem    %APPDATA%\REAPER\Effects\GreenStripe
rem
rem  mklink braucht Adminrechte (oder aktivierten
rem  Windows-Entwicklermodus). Das Skript startet bei Bedarf
rem  automatisch mit UAC-Anfrage neu.
rem
rem  Wichtig: Nur Datei-Inhalte laufen automatisch mit. Bei
rem  neuen, umbenannten oder geloeschten Dateien im Repo
rem  dieses Skript erneut ausfuehren - es setzt alle
rem  Verknuepfungen zurueck (alte Links werden ersetzt).
rem ============================================================

net session >nul 2>&1
if errorlevel 1 (
  echo Keine Adminrechte - Neustart mit UAC-Anfrage...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b 0
)

set "SRC=%~dp0"
set "DST=%APPDATA%\REAPER\Effects\GreenStripe"

echo Quelle: %SRC%
echo Ziel:   %DST%
echo.

if not exist "%DST%\" (
  echo Zielordner fehlt - wird angelegt...
  mkdir "%DST%" || goto :fail
)

set /a COUNT=0
set /a FAILS=0
for %%F in ("%SRC%*") do call :link "%%~nxF"

echo.
echo Fertig: %COUNT% Verknuepfungen gesetzt, %FAILS% Fehler.
pause
exit /b 0

:fail
echo FEHLER: Zielordner konnte nicht angelegt werden.
pause
exit /b 1

:link
set "name=%~1"
if /i "%name%"=="README.md" exit /b 0
if /i "%name%"=="make-reaper-links.cmd" exit /b 0
if exist "%DST%\%name%" del /f /q "%DST%\%name%"
mklink "%DST%\%name%" "%SRC%%name%" >nul
if errorlevel 1 (
  echo   FEHLER: %name%
  set /a FAILS+=1
) else (
  echo   OK: %name%
  set /a COUNT+=1
)
exit /b 0
