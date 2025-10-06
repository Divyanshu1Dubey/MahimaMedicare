@echo off
echo 🚀 Setting up Mahima Medicare for Development...

REM Create .env file from example if it doesn't exist
if not exist .env (
    echo 📋 Creating .env file from example...
    copy .env.example .env
    echo ✅ .env file created successfully!
    echo 📝 You may need to update the values in .env for your environment
) else (
    echo ✅ .env file already exists
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created!
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo 📦 Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo 🗄️  Setting up database...
python manage.py makemigrations
python manage.py migrate

echo.
echo 🎉 Setup complete! You can now run:
echo.
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo 🌐 Access the application at: http://127.0.0.1:8000
echo.
echo 👥 Test Credentials:
echo   Patient: p1 / test123
echo   Lab Tech: l1 / test123
echo.
pause