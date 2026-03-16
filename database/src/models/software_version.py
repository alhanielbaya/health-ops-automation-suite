from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class SoftwareVersion(Base):
    """Software installed on each asset."""
    __tablename__ = 'software_versions'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    
    # Software Details
    software_name = Column(String(200), nullable=False)
    version = Column(String(100))
    vendor = Column(String(100))
    license_key = Column(String(200))
    
    # Status & Compliance
    install_date = Column(DateTime)
    last_updated = Column(DateTime)
    is_required = Column(Boolean, default=False)
    is_compliant = Column(Boolean, default=True)
    
    # Healthcare-specific
    is_medical_device_software = Column(Boolean, default=False)
    fda_approved = Column(Boolean, default=False)
    validation_status = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="software_versions")
    
    def __repr__(self):
        return f"<SoftwareVersion(asset_id={self.asset_id}, software='{self.software_name}')>"
