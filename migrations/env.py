from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from models.tokens import Base

# This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# This section defines the SQLAlchemy database URL.
# Replace 'sqlite:///my_database.db' with your database URL.
config.set_main_option('sqlalchemy.url', 'sqlite:///my_database.db')

# Add your model's MetaData object here.
# This assumes you've imported your models and created the Base object in models/tokens.py.
target_metadata = Base.metadata

# Interpret the config options for SQLAlchemy to work with Alembic.
# Alembic will work with the 'autogenerate' feature based on comparison with this metadata.
def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Run migrations in 'online' mode.
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Check if we are running in 'online' or 'offline' mode and call the respective function.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
