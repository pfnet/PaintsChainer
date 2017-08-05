@echo off

SET path=%~dp0;%~dp0bin;%path%

SET vcvarsall="C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"

if exist %vcvarsall% (
    call %vcvarsall% amd64
) else (
    ECHO Microsoft Visual C++ Build Tools 2015 is not found, please install it via http://landinghub.visualstudio.com/visual-cpp-build-tools
)



SET LIB=%~dp0lib;%~dp0lib\x64;%LIB%
SET INCLUDE=%~dp0include;%INCLUDE%
SET LIBPATH=%~dp0lib;%~dp0lib\x64;%LIBPATH%

WHERE nvcc.exe
IF %ERRORLEVEL% NEQ 0 ECHO nvcc not found, please install CUDA via https://developer.nvidia.com/cuda-downloads


