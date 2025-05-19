@echo off
REM setup_environment.bat
REM
REM Script de configuración del entorno para ProjectPrompt en Windows
REM Este script automatiza la configuración del entorno para ProjectPrompt

echo === Configuración de Entorno para ProjectPrompt ===
echo ===================================================
echo.

REM Verificar Python
echo Verificando instalación de Python...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python no está instalado o no está en PATH.
    echo Por favor instala Python 3.8 o superior desde python.org
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación.
    exit /b 1
)

python --version
echo ✓ Python encontrado

REM Verificar pip
echo Verificando instalación de pip...
python -m pip --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo pip no está disponible. Instalando...
    python -m ensurepip --upgrade
)
echo ✓ pip está disponible

REM Crear entorno virtual
echo.
echo Creando entorno virtual...
python -m venv venv
echo ✓ Entorno virtual creado

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate
echo ✓ Entorno virtual activado

REM Actualizar pip
echo.
echo Actualizando pip...
python -m pip install --upgrade pip
echo ✓ pip actualizado a la última versión

REM Instalar dependencias
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo ✓ Dependencias instaladas correctamente

REM Crear archivo batch
echo.
echo Creando archivo de acceso directo...
echo @echo off > project-prompt.bat
echo "%~dp0venv\Scripts\python" "%~dp0project_prompt.py" %%* >> project-prompt.bat
echo ✓ Archivo batch project-prompt.bat creado

echo.
echo === Configuración completada ===
echo Para utilizar ProjectPrompt, prueba alguno de estos comandos:
echo project-prompt.bat --help
echo project-prompt.bat analyze .
echo project-prompt.bat init mi-proyecto
echo.
echo Para activar el entorno virtual en nuevas sesiones:
echo cd %CD% ^&^& call venv\Scripts\activate
echo.
echo ¡Gracias por usar ProjectPrompt!

REM Mantener la ventana abierta
pause
