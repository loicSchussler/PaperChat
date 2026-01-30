"""
Script pour créer les tables de la base de données
Exécuter avec: python create_db.py
"""
from app.database import engine, Base
from app.models import Paper, Chunk, QueryLog

print("Création des tables...")
Base.metadata.create_all(bind=engine)
print("Tables créées avec succès!")
