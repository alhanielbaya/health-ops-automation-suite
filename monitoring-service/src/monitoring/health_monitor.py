"""
Health Monitor - Core monitoring orchestrator.
Manages health checks for all assets in the database.
"""
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
import aiohttp
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of a health check."""
    asset_id: int
    check_type: str
    status: str  # 'healthy', 'warning', 'critical'
    response_time_ms: float
    is_reachable: bool
    error_message: Optional[str] = None
    details: Optional[Dict] = None


class HealthMonitor:
    """
    Main health monitoring orchestrator.
    
    This class manages:
    - Running health checks on assets
    - Measuring response times
    - Triggering alerts when thresholds are exceeded
    - Saving results to database
    """
    
    def __init__(self, config=None):
        """
        Initialize the health monitor.
        
        Args:
            config: MonitorConfig instance (uses defaults if None)
        """
        from .config import MonitorConfig
        from .alert_manager import AlertManager
        
        self.config = config or MonitorConfig()
        self.alert_manager = AlertManager()
        self._running = False
        self._check_interval = 30  # seconds between checks
        
        # Lazy load database session
        self._session = None
        logger.info("HealthMonitor initialized")
    
    @property
    def session(self):
        """Lazy load database session."""
        if self._session is None:
            # Add database path
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'database', 'src')
            if db_path not in sys.path:
                sys.path.insert(0, db_path)
            from models import get_session
            self._session = get_session()
        return self._session
    
    async def check_asset_health(self, asset) -> CheckResult:
        """
        Perform health check on a single asset.
        
        Args:
            asset: Asset model instance (needs id, asset_tag, hostname attributes)
        
        Returns:
            CheckResult with status and metrics
        """
        hostname = getattr(asset, 'hostname', None)
        if not hostname:
            logger.warning(f"Asset {getattr(asset, 'asset_tag', 'unknown')} has no hostname, skipping")
            return CheckResult(
                asset_id=getattr(asset, 'id', 0),
                check_type='connectivity',
                status='unknown',
                response_time_ms=0.0,
                is_reachable=False,
                error_message='No hostname configured'
            )
        
        # Ensure URL has protocol
        url = f"http://{hostname}" if not hostname.startswith(('http://', 'https://')) else hostname
        
        start_time = datetime.utcnow()
        
        try:
            # Perform HTTP check with timeout
            timeout = aiohttp.ClientTimeout(total=self.config.http_timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    end_time = datetime.utcnow()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    # Determine status based on response time
                    if response_time < self.config.warning_threshold_ms:
                        status = 'healthy'
                    elif response_time < self.config.critical_threshold_ms:
                        status = 'warning'
                    else:
                        status = 'critical'
                    
                    logger.info(f"Asset {asset.asset_tag}: {status} ({response_time:.2f}ms)")
                    
                    return CheckResult(
                        asset_id=asset.id,
                        check_type='http',
                        status=status,
                        response_time_ms=response_time,
                        is_reachable=True,
                        details={
                            'status_code': response.status,
                            'url': url,
                            'headers': dict(response.headers)
                        }
                    )
        
        except asyncio.TimeoutError:
            logger.error(f"Asset {asset.asset_tag}: Timeout after {self.config.http_timeout_seconds}s")
            return CheckResult(
                asset_id=asset.id,
                check_type='http',
                status='critical',
                response_time_ms=self.config.http_timeout_seconds * 1000,
                is_reachable=False,
                error_message=f'Timeout after {self.config.http_timeout_seconds} seconds'
            )
        
        except aiohttp.ClientError as e:
            logger.error(f"Asset {asset.asset_tag}: Connection error - {e}")
            return CheckResult(
                asset_id=asset.id,
                check_type='http',
                status='critical',
                response_time_ms=0.0,
                is_reachable=False,
                error_message=str(e)
            )
        
        except Exception as e:
            logger.error(f"Asset {asset.asset_tag}: Unexpected error - {e}")
            return CheckResult(
                asset_id=asset.id,
                check_type='http',
                status='critical',
                response_time_ms=0.0,
                is_reachable=False,
                error_message=f'Unexpected error: {str(e)}'
            )
    
    async def run_checks(self) -> List[CheckResult]:
        """
        Run health checks on all active assets.
        
        Returns:
            List of CheckResult for all assets
        """
        from models import Asset
        
        # Get all active assets from database
        assets = self.session.query(Asset).filter(Asset.status == 'active').all()
        
        if not assets:
            logger.warning("No active assets found to monitor")
            return []
        
        logger.info(f"Starting health checks for {len(assets)} assets...")
        
        # Run checks concurrently using asyncio.gather
        tasks = [self.check_asset_health(asset) for asset in assets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and process results
        check_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Check failed with exception: {result}")
                continue
            check_results.append(result)
            
            # Save to database
            self._save_check_result(result)
            
            # Check if alert needed
            if result.status in ['warning', 'critical']:
                await self.alert_manager.send_alert(
                    severity=result.status,
                    alert_type='health_check',
                    message=f"Asset check failed",
                    asset_id=result.asset_id,
                    details={
                        'response_time_ms': result.response_time_ms,
                        'error': result.error_message
                    }
                )
        
        logger.info(f"Completed {len(check_results)} health checks")
        return check_results
    
    def _save_check_result(self, result: CheckResult):
        """Save check result to database."""
        from models import HealthCheck
        
        try:
            health_check = HealthCheck(
                asset_id=result.asset_id,
                check_type=result.check_type,
                status=result.status,
                response_time_ms=result.response_time_ms,
                is_reachable=result.is_reachable,
                error_message=result.error_message,
                details=str(result.details) if result.details else None,
                threshold_warning_ms=self.config.warning_threshold_ms,
                threshold_critical_ms=self.config.critical_threshold_ms
            )
            self.session.add(health_check)
            self.session.commit()
        except Exception as e:
            logger.error(f"Failed to save health check: {e}")
            self.session.rollback()
    
    async def start_monitoring(self):
        """Start continuous monitoring loop."""
        self._running = True
        logger.info(f"Starting monitoring loop (interval: {self._check_interval}s)")
        
        while self._running:
            try:
                await self.run_checks()
                logger.info(f"Waiting {self._check_interval}s until next check...")
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short wait on error
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self._running = False
        logger.info("Monitoring stopped")
    
    def get_asset_status(self, asset_id: int) -> Optional[Dict]:
        """Get current status of an asset."""
        from models import HealthCheck
        
        latest_check = self.session.query(HealthCheck).filter(
            HealthCheck.asset_id == asset_id
        ).order_by(HealthCheck.checked_at.desc()).first()
        
        if not latest_check:
            return None
        
        return {
            'asset_id': asset_id,
            'status': latest_check.status,
            'response_time_ms': latest_check.response_time_ms,
            'last_checked': latest_check.checked_at.isoformat(),
            'is_reachable': latest_check.is_reachable,
            'error': latest_check.error_message
        }
    
    def get_all_status(self) -> List[Dict]:
        """Get status of all monitored assets."""
        from models import Asset
        
        assets = self.session.query(Asset).filter(Asset.status == 'active').all()
        results = []
        for asset in assets:
            status = self.get_asset_status(asset.id)
            if status:
                results.append(status)
        return results
