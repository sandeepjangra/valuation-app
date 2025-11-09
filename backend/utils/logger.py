"""
Request/Response Logger for ValuationApp Backend
Logs all incoming requests and outgoing responses with timestamps
"""

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging
import os

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure request/response logger
request_logger = logging.getLogger("valuation_app.requests")
request_logger.setLevel(logging.INFO)

# Create file handler for request logs
request_log_file = LOGS_DIR / "backend_requests.log"
request_handler = logging.FileHandler(request_log_file, encoding='utf-8')
request_handler.setLevel(logging.INFO)

# Create formatter for request logs
request_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
request_handler.setFormatter(request_formatter)
request_logger.addHandler(request_handler)

# Also add console handler for development
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(request_formatter)
request_logger.addHandler(console_handler)

class RequestResponseLogger:
    """Middleware for logging all API requests and responses"""
    
    def __init__(self):
        self.start_time = None
        self.request_id = None
    
    async def log_request(self, request: Request) -> Dict[str, Any]:
        """Log incoming request details"""
        self.start_time = time.time()
        self.request_id = f"{int(self.start_time * 1000)}"
        
        # Extract request body if present
        request_body = None
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                body_bytes = await request.body()
                if body_bytes:
                    request_body = body_bytes.decode('utf-8')
                    try:
                        # Try to parse as JSON for better formatting
                        request_body = json.loads(request_body)
                    except json.JSONDecodeError:
                        # Keep as string if not valid JSON
                        pass
        except Exception as e:
            request_body = f"Error reading body: {str(e)}"
        
        # Get query parameters
        query_params = dict(request.query_params) if request.query_params else None
        
        # Get headers (filter out sensitive ones)
        headers = dict(request.headers)
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        filtered_headers = {k: v for k, v in headers.items() 
                          if k.lower() not in sensitive_headers}
        
        request_data = {
            "request_id": self.request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": query_params,
            "headers": filtered_headers,
            "client_host": request.client.host if request.client else None,
            "request_body": request_body
        }
        
        # Log the request
        request_logger.info(f"REQUEST | {self.request_id} | {request.method} {request.url.path} | {json.dumps(request_data, indent=2)}")
        
        return request_data
    
    def log_response(self, response: Response, request_data: Dict[str, Any]) -> None:
        """Log outgoing response details"""
        if not self.start_time:
            return
        
        processing_time = (time.time() - self.start_time) * 1000  # in milliseconds
        
        # Extract response body if it's a JSONResponse
        response_body = None
        try:
            if hasattr(response, 'body') and response.body:
                if isinstance(response, JSONResponse):
                    # For JSONResponse, get the content
                    response_body = response.body.decode('utf-8')
                    try:
                        response_body = json.loads(response_body)
                    except json.JSONDecodeError:
                        pass
                else:
                    # For other responses, try to decode
                    response_body = response.body.decode('utf-8')[:1000]  # Limit size
        except Exception as e:
            response_body = f"Error reading response body: {str(e)}"
        
        response_data = {
            "request_id": self.request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": response.status_code,
            "processing_time_ms": round(processing_time, 2),
            "response_headers": dict(response.headers) if hasattr(response, 'headers') else None,
            "response_body": response_body
        }
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = "ERROR"
        elif response.status_code >= 400:
            log_level = "WARNING"
        else:
            log_level = "INFO"
        
        # Log the response
        getattr(request_logger, log_level.lower())(
            f"RESPONSE | {self.request_id} | {response.status_code} | {processing_time:.2f}ms | {json.dumps(response_data, indent=2)}"
        )

# Global logger instance
logger_instance = RequestResponseLogger()

async def log_request_middleware(request: Request):
    """Middleware function to log requests"""
    return await logger_instance.log_request(request)

def log_response_middleware(response: Response, request_data: Dict[str, Any]):
    """Middleware function to log responses"""
    logger_instance.log_response(response, request_data)

# Database operation logger
db_logger = logging.getLogger("valuation_app.database")
db_logger.setLevel(logging.INFO)

# Create file handler for database logs
db_log_file = LOGS_DIR / "backend_database.log"
db_handler = logging.FileHandler(db_log_file, encoding='utf-8')
db_handler.setLevel(logging.INFO)
db_handler.setFormatter(request_formatter)
db_logger.addHandler(db_handler)
db_logger.addHandler(console_handler)

class DatabaseLogger:
    """Logger for database operations"""
    
    @staticmethod
    def log_query(operation: str, collection: str, filter_dict: Optional[Dict] = None, 
                 result_count: Optional[int] = None, execution_time: Optional[float] = None):
        """Log database query operations"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "collection": collection,
            "filter": filter_dict,
            "result_count": result_count,
            "execution_time_ms": round(execution_time * 1000, 2) if execution_time else None
        }
        
        db_logger.info(f"DB_QUERY | {operation} | {collection} | {json.dumps(log_data, indent=2)}")
    
    @staticmethod
    def log_error(operation: str, collection: str, error: Exception):
        """Log database errors"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "collection": collection,
            "error": str(error),
            "error_type": type(error).__name__
        }
        
        db_logger.error(f"DB_ERROR | {operation} | {collection} | {json.dumps(log_data, indent=2)}")

# Export instances
db_logger_instance = DatabaseLogger()