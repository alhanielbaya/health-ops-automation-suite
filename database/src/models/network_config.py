from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class NetworkConfig(Base):
    """Network configuration for each asset."""
    __tablename__ = 'network_configs'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    
    # IP Configuration
    ip_address = Column(String(15))
    subnet_mask = Column(String(15))
    gateway = Column(String(15))
    dns_primary = Column(String(15))
    dns_secondary = Column(String(15))
    
    # Network Settings
    mac_address = Column(String(17))
    domain = Column(String(100))
    proxy_server = Column(String(200))
    vpn_configured = Column(Boolean, default=False)
    
    # Metadata
    config_type = Column(String(20), default='static')
    is_active = Column(Boolean, default=True)
    last_configured = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="network_configs")
    
    def __repr__(self):
        return f"<NetworkConfig(asset_id={self.asset_id}, ip='{self.ip_address}')>"
