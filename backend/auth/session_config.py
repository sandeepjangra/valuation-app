"""
Session and Token Configuration
"""

import os
from datetime import timedelta

class SessionConfig:
    # JWT Token Lifetimes
    ACCESS_TOKEN_LIFETIME = timedelta(hours=1)      # 1 hour
    REFRESH_TOKEN_LIFETIME = timedelta(days=30)     # 30 days
    
    # Session Inactivity Timeout
    INACTIVITY_TIMEOUT = timedelta(minutes=30)      # 30 minutes of inactivity
    
    # Auto-logout settings
    AUTO_LOGOUT_WARNING = timedelta(minutes=5)      # Warn 5 minutes before logout
    
    # Token refresh settings
    REFRESH_THRESHOLD = timedelta(minutes=10)       # Refresh when 10 minutes left
    
    @classmethod
    def get_session_timeout_seconds(cls) -> int:
        """Get session timeout in seconds for frontend"""
        return int(cls.INACTIVITY_TIMEOUT.total_seconds())
    
    @classmethod
    def get_warning_time_seconds(cls) -> int:
        """Get warning time in seconds for frontend"""
        return int(cls.AUTO_LOGOUT_WARNING.total_seconds())