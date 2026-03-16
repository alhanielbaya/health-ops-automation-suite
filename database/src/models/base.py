"""
Database base configuration.
All models import Base from here to avoid circular imports.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
