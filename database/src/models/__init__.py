"""
Database models for Health Ops Automation Suite.

This module defines all the SQLAlchemy models for tracking IT assets,
users, network configurations, software versions, and health monitoring.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import base first
from .base import Base

# Import all models (order matters for relationships)
from .user import User
from .asset import Asset
from .network_config import NetworkConfig
from .software_version import SoftwareVersion
from .health_check import HealthCheck, Alert

__all__ = [
    'Base',
    'Asset',
    'User',
    'NetworkConfig',
    'SoftwareVersion',
    'HealthCheck',
    'Alert',
    'get_engine',
    'init_db',
    'get_session'
]


def get_engine(db_path="sqlite:///health_ops.db"):
    """
    Create a SQLAlchemy engine for the database.
    
    Args:
        db_path: Path to SQLite database (default: health_ops.db in current directory)
    
    Returns:
        SQLAlchemy engine instance
    """
    return create_engine(db_path, echo=False)


def init_db(engine=None):
    """
    Initialize the database by creating all tables.
    
    Args:
        engine: SQLAlchemy engine (creates default if None)
    
    Returns:
        SQLAlchemy engine instance
    """
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"[OK] Database initialized: {engine.url}")
    return engine


def get_session(engine=None):
    """
    Get a database session for performing operations.
    
    Args:
        engine: SQLAlchemy engine (creates default if None)
    
    Returns:
        SQLAlchemy session instance
    
    Example:
        session = get_session()
        user = session.query(User).first()
        session.close()
    """
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
