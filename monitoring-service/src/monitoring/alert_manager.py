"""
Alert Manager - Handles all alerting logic.
Sends notifications when health checks fail.
"""
import logging
from typing import Dict, Optional
from datetime import datetime
import sys
import os

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages alerts for the monitoring system.
    
    Supports multiple notification methods:
    - Console logging
    - File logging
    - Webhook (for Slack, Teams, etc.)
    - Email (future implementation)
    """
    
    def __init__(self):
        """Initialize the alert manager."""
        self._session = None
        logger.info("AlertManager initialized")
    
    @property
    def session(self):
        """Lazy load database session."""
        if self._session is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'database', 'src')
            if db_path not in sys.path:
                sys.path.insert(0, db_path)
            from models import get_session
            self._session = get_session()
        return self._session
    
    async def send_alert(self, severity: str, alert_type: str, message: str, 
                        asset_id: int, details: Optional[Dict] = None):
        """
        Send an alert through all configured channels.
        
        Args:
            severity: 'warning' or 'critical'
            alert_type: Type of alert (e.g., 'health_check', 'threshold')
            message: Human-readable alert message
            asset_id: ID of the affected asset
            details: Additional context (dict)
        """
        # Log to console
        self._log_to_console(severity, message, details)
        
        # Save to database
        await self._save_to_database(severity, alert_type, message, asset_id, details)
        
        # Send webhook if configured (placeholder for future)
        await self._send_webhook(severity, message, asset_id, details)
    
    def _log_to_console(self, severity: str, message: str, details: Optional[Dict]):
        """Log alert to console with appropriate formatting."""
        if severity == 'critical':
            logger.critical(f"ALERT [CRITICAL]: {message}")
        elif severity == 'warning':
            logger.warning(f"ALERT [WARNING]: {message}")
        else:
            logger.info(f"ALERT [INFO]: {message}")
        
        if details:
            logger.info(f"  Details: {details}")
    
    async def _save_to_database(self, severity: str, alert_type: str, 
                               message: str, asset_id: int, 
                               details: Optional[Dict]):
        """Save alert to database for tracking."""
        from models import Alert, HealthCheck
        
        try:
            # Find the most recent health check for this asset
            health_check = self.session.query(HealthCheck).filter(
                HealthCheck.asset_id == asset_id
            ).order_by(HealthCheck.checked_at.desc()).first()
            
            alert = Alert(
                health_check_id=health_check.id if health_check else None,
                severity=severity,
                alert_type=alert_type,
                message=message,
                notification_sent=True,
                notification_method='console',
                notification_sent_at=datetime.utcnow()
            )
            
            self.session.add(alert)
            self.session.commit()
            logger.info(f"Alert saved to database (ID: {alert.id})")
            
        except Exception as e:
            logger.error(f"Failed to save alert to database: {e}")
            self.session.rollback()
    
    async def _send_webhook(self, severity: str, message: str, 
                           asset_id: int, details: Optional[Dict]):
        """
        Send alert to webhook (Slack, Teams, etc.).
        
        This is a placeholder for future implementation.
        """
        # TODO: Implement webhook integration
        pass
    
    def get_recent_alerts(self, limit: int = 10) -> list:
        """Get recent alerts from database."""
        from models import Alert
        
        return self.session.query(Alert).order_by(
            Alert.created_at.desc()
        ).limit(limit).all()
    
    def get_unresolved_alerts(self) -> list:
        """Get all unresolved alerts."""
        from models import Alert
        
        return self.session.query(Alert).filter(
            Alert.is_resolved == False
        ).order_by(Alert.created_at.desc()).all()
    
    def resolve_alert(self, alert_id: int, resolved_by: str, 
                     notes: Optional[str] = None) -> bool:
        """Mark an alert as resolved."""
        from models import Alert
        
        try:
            alert = self.session.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.is_resolved = True
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = resolved_by
                alert.resolution_notes = notes
                self.session.commit()
                logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            self.session.rollback()
            return False
