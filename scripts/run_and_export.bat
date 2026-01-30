@echo off
setlocal enabledelayedexpansion
set ROOT=%~dp0..\..
echo Root: %ROOT%

echo Running demo to generate CSV...
python "%ROOT%\A_MCM_A\demo_run.py"

echo Exporting notebook to HTML...
set NOTEBOOK=%ROOT%\A_MCM_A\notebooks\battery_csv_demo.ipynb
set OUTPUT=%ROOT%\A_MCM_A\notebooks\battery_csv_demo.html
python -m nbconvert --to html --execute "%NOTEBOOK%" --output "%OUTPUT%" --ExecutePreprocessor.timeout=600

echo HTML exported to: %OUTPUT%
