"""
Login Activity Logger
Logs all login attempts, successes, and failures with detailed information
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pathlib import Path

class LoginLogger:
    def __init__(self, log_file_path: Optional[str] = None):
        """Initialize login logger with log file path"""
        if log_file_path is None:
            # Default to logs directory in project root
            project_root = Path(__file__).parent.parent.parent
            logs_dir = project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            log_file_path = logs_dir / "login_activities.log"
        
        self.log_file_path = Path(log_file_path)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        jwt_token: Optional[str] = None,
        organization_id: Optional[str] = None,
        role: Optional[str] = None,
        error_message: Optional[str] = None,
        login_type: str = "traditional"
    ) -> None:
        """
        Log a login attempt with all relevant details
        
        Args:
            email: User email attempting login
            success: Whether login was successful
            ip_address: Client IP address
            user_agent: Client user agent
            jwt_token: Generated JWT token (first 20 chars for security)
            organization_id: User's organization
            role: User's role
            error_message: Error message if login failed
            login_type: Type of login (traditional, dev, admin_quick)
        """
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "email": email,
            "success": success,
            "login_type": login_type,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "organization_id": organization_id,
            "role": role
        }
        
        if success and jwt_token:
            # Only log first 20 characters of JWT for security
            log_entry["jwt_token_preview"] = jwt_token[:20] + "..."
            log_entry["jwt_length"] = len(jwt_token)
        
        if not success and error_message:
            log_entry["error_message"] = error_message
        
        # Write to log file
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            # Don't fail the login process if logging fails
            print(f"Failed to write login log: {e}")
    
    def get_recent_login_activities(self, limit: int = 100) -> list:
        """
        Get recent login activities from log file
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent login activities
        """
        activities = []
        
        try:
            if not self.log_file_path.exists():
                return activities
            
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Get last 'limit' lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            for line in recent_lines:
                try:
                    activity = json.loads(line.strip())
                    activities.append(activity)
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"Failed to read login log: {e}")
        
        return activities
    
    def get_login_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get login statistics for the last N hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with login statistics
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        activities = self.get_recent_login_activities(limit=1000)
        
        # Filter activities within time range
        recent_activities = []
        for activity in activities:
            try:
                activity_time = datetime.fromisoformat(activity['timestamp'])
                if activity_time >= cutoff_time:
                    recent_activities.append(activity)
            except (KeyError, ValueError):
                continue
        
        # Calculate statistics
        total_attempts = len(recent_activities)
        successful_logins = sum(1 for a in recent_activities if a.get('success', False))
        failed_logins = total_attempts - successful_logins
        
        # Unique users
        unique_users = len(set(a.get('email', '') for a in recent_activities))
        
        # Login types
        login_types = {}
        for activity in recent_activities:
            login_type = activity.get('login_type', 'unknown')
            login_types[login_type] = login_types.get(login_type, 0) + 1
        
        return {
            "time_range_hours": hours,
            "total_attempts": total_attempts,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "success_rate": (successful_logins / total_attempts * 100) if total_attempts > 0 else 0,
            "unique_users": unique_users,
            "login_types": login_types
        }

# Global login logger instance
login_logger = LoginLogger()