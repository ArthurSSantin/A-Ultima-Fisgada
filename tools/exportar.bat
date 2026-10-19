@echo off
rem Gera build\AUltimaFisgada.exe a partir do projeto.
rem Rode de novo sempre que o jogo mudar: o .exe e uma copia fechada do projeto
rem no momento da exportacao e nao se atualiza sozinho.
setlocal
cd /d "%~dp0.."

set "GODOT="
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\GodotEngine.GodotEngine_*") do (
	if exist "%%D\Godot_v4.7.2-stable_win64_console.exe" set "GODOT=%%D\Godot_v4.7.2-stable_win64_console.exe"
)
if not defined GODOT (
	echo Godot 4.7.2 nao encontrado. Instale com: winget install GodotEngine.GodotEngine
	pause
	exit /b 1
)
if not exist export_presets.cfg (
	echo Falta o export_presets.cfg. No Godot: Project ^> Export ^> Add ^> Windows Desktop.
	pause
	exit /b 1
)

if not exist build mkdir build
"%GODOT%" --headless --path . --export-release "Windows Desktop" build/AUltimaFisgada.exe
if errorlevel 1 (
	echo A exportacao falhou.
	pause
	exit /b 1
)
echo Pronto: build\AUltimaFisgada.exe
pause
