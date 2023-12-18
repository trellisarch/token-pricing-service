from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.tokens import Base

engine = create_engine('sqlite:///my_database.db')  # Example: SQLite database
Session = sessionmaker(bind=engine)
session = Session()

# Create tables
Base.metadata.create_all(engine)
