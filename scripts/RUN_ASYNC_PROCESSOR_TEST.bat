@echo off
echo ========================================
echo    AI Teddy Bear - Async Processor Test
echo ========================================
echo.

REM Set the Python path to include the src directory
set PYTHONPATH=%CD%\src;%PYTHONPATH%

echo [1/4] Installing required packages...
pip install -r requirements_async_processing.txt

echo.
echo [2/4] Running basic functionality test...
python -m pytest test_async_processor.py::TestAdvancedAsyncProcessor::test_submit_and_process_task -v

echo.
echo [3/4] Running performance test...
python -m pytest test_async_processor.py::TestPerformance::test_concurrent_task_processing -v

echo.
echo [4/4] Running full integration test...
python -m pytest test_async_processor.py::test_full_workflow -v

echo.
echo ========================================
echo Testing complete! Check results above.
echo ========================================
echo.
echo Press any key to run the full test suite...
pause >nul

echo.
echo Running complete test suite...
python -m pytest test_async_processor.py -v --tb=short

echo.
echo ========================================
echo All tests completed!
echo ========================================
pause 