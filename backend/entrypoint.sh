#!/bin/bash
set -e

echo "Starting PaperChat Backend..."

# Initialiser la base de données
echo "Initializing database..."
python init_db.py

# Lancer le serveur FastAPI
echo "Starting FastAPI server..."
exec "$@"
