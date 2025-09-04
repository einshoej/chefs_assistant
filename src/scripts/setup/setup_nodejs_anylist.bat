@echo off
echo ============================================
echo Setting up Node.js AnyList Integration
echo ============================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed!
    echo Please download and install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Node.js found: 
node --version
echo.

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed!
    echo Please ensure npm is installed with Node.js
    echo.
    pause
    exit /b 1
)

echo npm found:
npm --version
echo.

REM Navigate to the nodejs directory
cd /d "%~dp0..\..\anylist_integration\nodejs"

if not exist package.json (
    echo ERROR: package.json not found!
    echo Please ensure the Node.js bridge files are in place
    echo.
    pause
    exit /b 1
)

echo Installing npm dependencies...
npm install

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✅ Setup completed successfully!
    echo ============================================
    echo.
    echo The official AnyList package is now installed.
    echo You can now use the AnyListOfficialClient in your Python code.
    echo.
) else (
    echo.
    echo ============================================
    echo ❌ Setup failed!
    echo ============================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
