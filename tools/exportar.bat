@echo off
rem Gera build\AUltimaFisgada.exe a partir do projeto e abre o jogo.
rem Rode de novo sempre que o jogo mudar: o .exe e uma copia fechada do projeto
rem no momento da exportacao e nao se atualiza sozinho.
setlocal
cd /d "%~dp0.."
title Exportando A Ultima Fisgada

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
rem Apaga o .exe antigo para nao abrir uma copia velha se a exportacao falhar.
rem Se ele nao some, esta em uso: com o jogo aberto o Windows trava o arquivo.
:apagar_exe
if exist build\AUltimaFisgada.exe del /f /q build\AUltimaFisgada.exe 2> nul
if exist build\AUltimaFisgada.exe (
	echo O jogo esta aberto. Feche a janela do jogo e aperte uma tecla para continuar.
	pause > nul
	goto apagar_exe
)

echo Exportando o jogo, aguarde uns segundos...
"%GODOT%" --headless --path . --export-release "Windows Desktop" build/AUltimaFisgada.exe > build\exportar.log 2>&1
if errorlevel 1 (
	echo A exportacao falhou. Detalhes em build\exportar.log
	pause
	exit /b 1
)
if not exist build\AUltimaFisgada.exe (
	echo O .exe nao foi gerado. Detalhes em build\exportar.log
	pause
	exit /b 1
)

echo Pronto: build\AUltimaFisgada.exe
echo Abrindo a pasta e o jogo...
start "" explorer.exe "%CD%\build"
start "" "%CD%\build\AUltimaFisgada.exe"
"%SystemRoot%\System32\timeout.exe" /t 3 > nul
