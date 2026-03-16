from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Asset(Base):
    """IT asset (computer, server, device) tracking."""
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    asset_tag = Column(String(50), unique=True, nullable=False)
    asset_type = Column(String(50), nullable=False)
    hostname = Column(String(100))
    serial_number = Column(String(100))
    manufacturer = Column(String(100))
    model = Column(String(100))
    status = Column(String(20), default='active')
    location = Column(String(200))
    department = Column(String(100))
    purchase_date = Column(DateTime)
    warranty_expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="assets")
    network_configs = relationship("NetworkConfig", back_populates="asset", cascade="all, delete-orphan")
    software_versions = relationship("SoftwareVersion", back_populates="asset", cascade="all, delete-orphan")
    health_checks = relationship("HealthCheck", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Asset(asset_tag='{self.asset_tag}', type='{self.asset_type}')>"
