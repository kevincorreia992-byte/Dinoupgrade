@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3"
) else (
  set "PY=python"
)
%PY% -c "import pygame" >nul 2>&1
if errorlevel 1 (
  echo Instalando o Pygame (necessita de internet)...
  %PY% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Falha ao instalar as dependencias. Verifique o Python e a internet.
    pause
    exit /b 1
  )
)
%PY% main.py
if errorlevel 1 (
  echo O jogo encontrou um erro. Veja a mensagem acima.
  pause
)
endlocal
