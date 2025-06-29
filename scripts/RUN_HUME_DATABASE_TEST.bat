@echo off
echo 🎤 HUME AI + Database Integration Test
echo =====================================

echo 📋 Installing required packages...
pip install sqlalchemy alembic hume python-dotenv numpy soundfile

echo.
echo 🗄️ Setting up database...
python database.py

echo.
echo 🧪 Running comprehensive test...
python test_hume_database.py

echo.
echo ✅ Test completed! Check the generated files:
echo   📁 Database: data/emotion.db
echo   📄 Reports: child_report_*.json
echo   🎵 Audio: sample_*.wav
echo   📊 Predictions: batch_predictions.json

pause 