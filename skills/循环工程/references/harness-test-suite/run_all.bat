@echo off
chcp 65001 >nul
where python >nul 2>nul && set PYTHON=python
if not defined PYTHON (where py >nul 2>nul && set PYTHON=py)
if not defined PYTHON (echo 未找到 python 解释器 & exit /b 1)
%PYTHON% "%~dp0run_all.py"
exit /b %errorlevel%
