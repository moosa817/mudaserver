from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys

# Adjust this import to fit your project structure
from app.core.database import Base, DATABASE_URL  # Import Base (and DATABASE_URL)
from app.models.user import User  # Import the User model (from the correct path)

sys.path.append(".")  # Ensures the application is in the module search path

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name:
    fileConfig(config.config_file_name)

# Tell Alembic to use the metadata from Base, which now includes User model
target_metadata = (
    Base.metadata
)  # Base.metadata will include all models (including User)


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,  # Pass the metadata to Alembic
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
