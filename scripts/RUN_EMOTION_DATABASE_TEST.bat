@echo off
echo ========================================
echo  AI Teddy Bear - Emotion Database Test
echo ========================================
echo.

REM Set the Python path to include the src directory
set PYTHONPATH=%CD%\src;%PYTHONPATH%

echo [1/5] Installing required packages...
pip install -r requirements_emotion_database.txt

echo.
echo [2/5] Running basic database integration test...
python -m pytest test_emotion_database_integration.py::TestDatabaseEmotionService::test_analyze_and_save_basic -v

echo.
echo [3/5] Running emotion analytics test...
python -m pytest test_emotion_database_integration.py::TestDatabaseEmotionService::test_emotion_analytics -v

echo.
echo [4/5] Running parental report test...
python -m pytest test_emotion_database_integration.py::TestDatabaseEmotionService::test_parental_report_generation -v

echo.
echo [5/5] Running convenience functions test...
python -m pytest test_emotion_database_integration.py::TestConvenienceFunctions -v

echo.
echo ========================================
echo Core tests complete! Check results above.
echo ========================================
echo.
echo Press any key to run the full integration test suite...
pause >nul

echo.
echo Running complete integration test suite...
python test_emotion_database_integration.py

echo.
echo ========================================
echo Running pytest with detailed output...
echo ========================================
python -m pytest test_emotion_database_integration.py -v --tb=short

echo.
echo ========================================
echo Testing database performance...
echo ========================================
python -m pytest test_emotion_database_integration.py::TestPerformanceAndLoad -v

echo.
echo ========================================
echo All emotion database tests completed!
echo ========================================
echo.
echo Test Summary:
echo - Basic emotion analysis and storage
echo - Emotion history retrieval
echo - Analytics and insights generation
echo - Parental reporting
echo - Performance and load testing
echo - Convenience functions
echo.
pause 