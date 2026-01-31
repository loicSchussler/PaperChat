"""
Script to run database migrations
"""
import sys
from pathlib import Path
from sqlalchemy import text
from app.database import engine

def run_migration(sql_file: str):
    """Execute a SQL migration file"""
    sql_path = Path(__file__).parent / "migrations" / sql_file

    if not sql_path.exists():
        print(f"Error: Migration file not found: {sql_path}")
        sys.exit(1)

    print(f"Reading migration file: {sql_path}")
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print("Executing migration...")
    try:
        with engine.connect() as connection:
            # Split SQL by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]

            for i, statement in enumerate(statements, 1):
                print(f"Executing statement {i}/{len(statements)}...")
                connection.execute(text(statement))

            connection.commit()

        print("✓ Migration completed successfully!")

    except Exception as e:
        print(f"✗ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration("create_conversations.sql")
