from src.aee.infrastructure.database import db_config

if __name__ == "__main__":
    print("Initializing database...")
    db_config.create_all()
    print("Database initialization complete.")
