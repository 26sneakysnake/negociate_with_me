#!/bin/bash
# Backend startup script with database initialization

echo "🚀 Starting NegotiAI Backend..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if python3 -c "from database import engine; engine.connect()" 2>/dev/null; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts - PostgreSQL not ready yet..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Failed to connect to PostgreSQL after $max_attempts attempts"
    exit 1
fi

# Initialize database tables and templates
echo "📦 Initializing database..."
python3 init_database.py

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi

# Start the FastAPI server
echo "🎯 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
