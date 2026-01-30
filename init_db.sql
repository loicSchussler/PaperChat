-- Initialisation de la base de données avec extension pgvector

-- Créer l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- La création des tables sera gérée par Alembic/SQLAlchemy
