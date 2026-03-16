from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class HealthCheck(Base):
    """Monitoring results from health monitoring service."""
    __tablename__ = 'health_checks'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'), nullable=False)
    
    # Check Results
    check_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    response_time_ms = Column(Float)
    
    # Detailed Results
    is_reachable = Column(Boolean)
    error_message = Column(String(500))
    details = Column(String(1000))
    
    # Thresholds
    threshold_warning_ms = Column(Float, default=1000.0)
    threshold_critical_ms = Column(Float, default=5000.0)
    
    # Timestamps
    checked_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="health_checks")
    alerts = relationship("Alert", back_populates="health_check", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<HealthCheck(asset_id={self.asset_id}, type='{self.check_type}', status='{self.status}')>"


class Alert(Base):
    """Alerts triggered when health checks fail."""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    health_check_id = Column(Integer, ForeignKey('health_checks.id'), nullable=False)
    
    # Alert Details
    severity = Column(String(20), nullable=False)
    alert_type = Column(String(50), nullable=False)
    message = Column(String(500), nullable=False)
    
    # Notification Tracking
    notification_sent = Column(Boolean, default=False)
    notification_method = Column(String(50))
    notification_sent_at = Column(DateTime)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolution_notes = Column(String(1000))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    health_check = relationship("HealthCheck", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(severity='{self.severity}', type='{self.alert_type}', resolved={self.is_resolved})>"
