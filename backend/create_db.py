"""
Script to create database tables
Run with: python create_db.py
"""
from app.database import engine, Base
from app.models import Paper, Chunk, QueryLog

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
