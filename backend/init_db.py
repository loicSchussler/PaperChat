"""
Script d'initialisation complète de la base de données
Combine la création des tables et l'exécution des migrations
"""
import sys
import time
from pathlib import Path
from sqlalchemy import text
from app.database import engine, Base

def wait_for_db(max_retries=30, retry_interval=1):
    """Attendre que la base de données soit prête"""
    print("Waiting for database to be ready...")
    for i in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database is ready!")
            return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"Database not ready yet (attempt {i+1}/{max_retries}), waiting...")
                time.sleep(retry_interval)
            else:
                print(f"Failed to connect to database after {max_retries} attempts: {e}")
                return False
    return False

def create_tables():
    """Créer les tables de base (papers, chunks, query_logs)"""
    print("\n1. Creating base tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Base tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

def run_migration(sql_file: str):
    """Exécuter un fichier de migration SQL"""
    sql_path = Path(__file__).parent / "migrations" / sql_file

    if not sql_path.exists():
        print(f"Warning: Migration file not found: {sql_path}")
        return True  # Ne pas bloquer si le fichier n'existe pas

    print(f"\n2. Running migration: {sql_file}")
    try:
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        with engine.connect() as connection:
            # Diviser le SQL par points-virgules et exécuter chaque instruction
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]

            for i, statement in enumerate(statements, 1):
                print(f"  Executing statement {i}/{len(statements)}...")
                connection.execute(text(statement))

            connection.commit()

        print("✓ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"✗ Error during migration: {e}")
        return False

def main():
    """Initialisation complète de la base de données"""
    print("=" * 60)
    print("PaperChat - Database Initialization")
    print("=" * 60)

    # Attendre que la DB soit prête
    if not wait_for_db():
        sys.exit(1)

    # Créer les tables de base
    if not create_tables():
        sys.exit(1)

    # Exécuter les migrations
    if not run_migration("create_conversations.sql"):
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ Database initialization completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
