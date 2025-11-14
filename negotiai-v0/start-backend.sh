#!/bin/bash
# Quick start script for backend (without Docker)

cd backend

echo "🔧 Installing dependencies..."
pip3 install -q -r requirements.txt

echo "🗄️ Initializing database with SQLite..."
python3 init_db.py

echo "🚀 Starting backend server..."
python3 main.py
