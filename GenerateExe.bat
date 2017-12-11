rd dist /S
rd build /S
pyinstaller main.py
cd resourse\
xcopy * ..\dist\main\resourse\ /H /E /G /Q /R /Y
cd ..\keys\
xcopy * ..\dist\main\keys\ /H /E /G /Q /R /Y
cd ..\dist\main\PyQt5\Qt\plugins\platforms\
xcopy * ..\..\..\..\platforms\ /H /E /G /Q /R /Y
pause