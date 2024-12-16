@echo off

REM Path to your Conda executable (adjust if necessary)
REM set CONDA_EXE=C:\Users\YourUsername\Anaconda3\Scripts\activate.bat

REM Path to your Conda environment
set current_dir=%~dp0

set CONDA_ENV_PATH=%current_dir%env
REM Path to your Python script
set SCRIPT_PATH_1=src\app\main.py
set SCRIPT_PATH_2=src\app\main_backend.py
set SCRIPT_PATH_3=src\app\main_update.py
set SCRIPT_PATH_4=src\app\main_status.py

REM Open first terminal
start "Terminal 1" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_1%""

REM Open second terminal
start "Terminal 2" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_2%""

REM Open third terminal
start "Terminal 3" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_3%""

REM Open fourth terminal
start "Terminal 4" cmd /k "call conda activate "%CONDA_ENV_PATH%" && python "%SCRIPT_PATH_4%""
