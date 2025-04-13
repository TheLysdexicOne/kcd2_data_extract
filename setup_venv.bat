@echo off
echo Creating a fresh virtual environment...

:: Remove existing .venv directory if it exists
if exist .venv (
    echo Removing existing virtual environment...
    rmdir /s /q .venv
)

:: Create a new virtual environment
echo Creating new virtual environment...
python -m venv .venv

:: Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install required packages
echo Installing required packages...
pip install -r requirements.txt
pip install vulture mypy pytest

echo.
echo Virtual environment setup complete!
echo You can now run:
echo   vulture .
echo   mypy .
echo.
echo Press any key to exit...
pause > nul