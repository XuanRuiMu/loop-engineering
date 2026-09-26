@echo off
setlocal
chcp 65001 >nul
where python >nul 2>nul && goto :python
where py >nul 2>nul && goto :py
echo 未找到可用 Python 解释器
exit /b 1
:python
python -B "%~dp0run_all.py"
exit /b %errorlevel%
:py
py -3 -B "%~dp0run_all.py"
exit /b %errorlevel%
