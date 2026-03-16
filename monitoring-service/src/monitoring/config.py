"""
Configuration for the monitoring service.
Centralizes all configurable parameters.
"""
import os
from dataclasses import dataclass


@dataclass
class MonitorConfig:
    """Configuration for the Health Monitor."""
    
    # HTTP Check Settings
    http_timeout_seconds: int = 10
    
    # Latency Thresholds (milliseconds)
    warning_threshold_ms: float = 1000.0
    critical_threshold_ms: float = 5000.0
    
    # Monitoring Interval
    check_interval_seconds: int = 30
    
    # Alert Settings
    alert_on_warning: bool = True
    max_alert_history: int = 1000
    
    # Retry Settings
    max_retries: int = 3
    retry_delay_seconds: int = 2
    
    def __post_init__(self):
        """Override defaults with environment variables if present."""
        http_timeout = os.getenv('MONITOR_HTTP_TIMEOUT')
        if http_timeout:
            self.http_timeout_seconds = int(http_timeout)
        
        warning_threshold = os.getenv('MONITOR_WARNING_THRESHOLD')
        if warning_threshold:
            self.warning_threshold_ms = float(warning_threshold)
        
        critical_threshold = os.getenv('MONITOR_CRITICAL_THRESHOLD')
        if critical_threshold:
            self.critical_threshold_ms = float(critical_threshold)
        
        check_interval = os.getenv('MONITOR_CHECK_INTERVAL')
        if check_interval:
            self.check_interval_seconds = int(check_interval)
