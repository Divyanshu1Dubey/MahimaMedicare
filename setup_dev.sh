#!/bin/bash

echo "🚀 Setting up Mahima Medicare for Development..."

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from example..."
    cp .env.example .env
    echo "✅ .env file created successfully!"
    echo "📝 You may need to update the values in .env for your environment"
else
    echo "✅ .env file already exists"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

pip install -r requirements.txt

echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "🎉 Setup complete! You can now run:"
echo ""
echo "For Windows:"
echo "  venv\\Scripts\\activate"
echo "  python manage.py runserver"
echo ""
echo "For Linux/Mac:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "🌐 Access the application at: http://127.0.0.1:8000"
echo ""
echo "👥 Test Credentials:"
echo "  Patient: p1 / test123"
echo "  Lab Tech: l1 / test123"
echo ""