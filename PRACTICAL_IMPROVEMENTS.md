# Practical Code Improvements

This document provides specific, actionable code improvements that can be implemented immediately.

## 1. Fix Bare Exception Handlers

### File: `new_signup.py`

**Current Code (Lines 33-34, 39-40):**
```python
try:
    os.system(f'taskkill /F /PID {pid} /T 2>nul')
except:
    pass
```

**Improved Code:**
```python
try:
    os.system(f'taskkill /F /PID {pid} /T 2>nul')
except (OSError, subprocess.SubprocessError, ValueError) as e:
    # Process may already be terminated or invalid PID
    logger.debug(f"Failed to kill process {pid}: {e}")
except Exception as e:
    logger.warning(f"Unexpected error killing process {pid}: {e}")
```

### File: `new_signup.py` - Line 387

**Current Code:**
```python
except:
    return False
```

**Improved Code:**
```python
except (AttributeError, TypeError, ValueError) as e:
    logger.error(f"Error in fill_password: {e}", exc_info=True)
    return False
except Exception as e:
    logger.error(f"Unexpected error in fill_password: {e}", exc_info=True)
    return False
```

## 2. Improve Password Generation Security

### File: `new_signup.py` - Line 390-393

**Current Code:**
```python
def generate_password(length=12):
    """Generate random password"""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(random.choices(chars, k=length))
```

**Improved Code:**
```python
import secrets
import string

def generate_password(length=12):
    """Generate cryptographically secure random password
    
    Args:
        length: Password length (default: 12, minimum: 8)
        
    Returns:
        str: Cryptographically secure random password
    """
    if length < 8:
        length = 8  # Enforce minimum length
    
    # Use secrets module for cryptographically secure randomness
    chars = string.ascii_letters + string.digits + string.punctuation
    # Remove ambiguous characters that might cause confusion
    chars = chars.replace('0', '').replace('O', '').replace('l', '').replace('I', '')
    
    return ''.join(secrets.choice(chars) for _ in range(length))
```

## 3. Add Proper Logging

### Create: `core/logger.py`

```python
"""Logging configuration for Cursor Free VIP"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_console: bool = True
) -> logging.Logger:
    """Setup application-wide logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        enable_console: Whether to enable console logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('cursor_free_vip')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create default logger instance
logger = setup_logging()
```

## 4. Improve Error Handling with Custom Exceptions

### Create: `core/exceptions.py`

```python
"""Custom exception classes for Cursor Free VIP"""

class CursorFreeVIPError(Exception):
    """Base exception for all Cursor Free VIP errors"""
    pass

class ConfigError(CursorFreeVIPError):
    """Configuration-related errors"""
    pass

class AuthError(CursorFreeVIPError):
    """Authentication-related errors"""
    pass

class TokenError(AuthError):
    """Token-related errors"""
    pass

class BrowserError(CursorFreeVIPError):
    """Browser automation errors"""
    pass

class FileOperationError(CursorFreeVIPError):
    """File operation errors"""
    pass

class DatabaseError(CursorFreeVIPError):
    """Database operation errors"""
    pass
```

## 5. Improve Type Hints

### File: `utils.py` - Example

**Current Code:**
```python
def get_user_documents_path():
    """Get user documents path"""
```

**Improved Code:**
```python
from typing import Optional
from pathlib import Path

def get_user_documents_path() -> Path:
    """Get user documents path
    
    Returns:
        Path object pointing to user's Documents directory
        
    Raises:
        OSError: If Documents directory cannot be determined
    """
    # Implementation...
```

## 6. Add Input Validation

### File: `manual_custom_auth.py` - Token Input

**Current Code:**
```python
token = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
if not token:
    print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('manual_auth.token_required')}{Style.RESET_ALL}")
    return
```

**Improved Code:**
```python
def validate_token(token: str) -> tuple[bool, Optional[str]]:
    """Validate token format
    
    Args:
        token: Token string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not token:
        return False, "Token cannot be empty"
    
    if len(token) < 10:
        return False, "Token appears to be too short"
    
    # Basic JWT format check (if applicable)
    if token.count('.') == 2:
        parts = token.split('.')
        if len(parts[0]) < 10 or len(parts[1]) < 10:
            return False, "Token format appears invalid"
    
    return True, None

# Usage:
token = input(f"{Fore.CYAN}> {Style.RESET_ALL}").strip()
is_valid, error_msg = validate_token(token)
if not is_valid:
    print(f"{Fore.RED}{EMOJI['ERROR']} {error_msg or translator.get('manual_auth.token_required')}{Style.RESET_ALL}")
    return
```

## 7. Improve Database Connection Handling

### File: `cursor_auth.py`

**Current Code:**
```python
conn = sqlite3.connect(self.db_path)
```

**Improved Code:**
```python
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def get_db_connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """Context manager for database connections
    
    Args:
        db_path: Path to SQLite database
        
    Yields:
        sqlite3.Connection: Database connection
        
    Raises:
        DatabaseError: If connection cannot be established
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA journal_mode = WAL")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Database operation failed: {e}") from e
    finally:
        if conn:
            conn.close()

# Usage:
def update_auth(self, email=None, access_token=None, refresh_token=None, auth_type="Auth_0"):
    try:
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            # ... perform operations
    except DatabaseError as e:
        logger.error(f"Failed to update auth: {e}")
        return False
```

## 8. Add Configuration Validation

### Create: `core/config_validator.py`

```python
"""Configuration validation utilities"""
from configparser import ConfigParser
from typing import Dict, List, Tuple
from pathlib import Path
import os

class ConfigValidator:
    """Validate configuration values"""
    
    @staticmethod
    def validate_path(path_str: str, must_exist: bool = False) -> Tuple[bool, Optional[str]]:
        """Validate a file or directory path
        
        Args:
            path_str: Path string to validate
            must_exist: Whether the path must exist
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path_str:
            return False, "Path cannot be empty"
        
        try:
            path = Path(path_str)
            if must_exist and not path.exists():
                return False, f"Path does not exist: {path_str}"
            return True, None
        except Exception as e:
            return False, f"Invalid path format: {e}"
    
    @staticmethod
    def validate_timing_range(timing_str: str) -> Tuple[bool, Optional[str]]:
        """Validate timing range format (e.g., '0.5-1.5' or '0.5,1.5')
        
        Args:
            timing_str: Timing string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not timing_str:
            return False, "Timing value cannot be empty"
        
        try:
            if '-' in timing_str:
                min_val, max_val = map(float, timing_str.split('-'))
            elif ',' in timing_str:
                min_val, max_val = map(float, timing_str.split(','))
            else:
                min_val = max_val = float(timing_str)
            
            if min_val < 0 or max_val < 0:
                return False, "Timing values must be non-negative"
            if min_val > max_val:
                return False, "Minimum timing must be <= maximum timing"
            
            return True, None
        except ValueError:
            return False, f"Invalid timing format: {timing_str}"
    
    @staticmethod
    def validate_config(config: ConfigParser) -> Tuple[bool, List[str]]:
        """Validate entire configuration
        
        Args:
            config: ConfigParser instance to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate browser paths
        if config.has_section('Browser'):
            browsers = ['chrome', 'edge', 'firefox', 'brave', 'opera']
            for browser in browsers:
                path_key = f'{browser}_path'
                if config.has_option('Browser', path_key):
                    path = config.get('Browser', path_key)
                    is_valid, error = ConfigValidator.validate_path(path, must_exist=False)
                    if not is_valid:
                        errors.append(f"Browser.{path_key}: {error}")
        
        # Validate timing values
        if config.has_section('Timing'):
            timing_keys = [
                'min_random_time', 'max_random_time', 'page_load_wait',
                'input_wait', 'submit_wait', 'verification_code_input'
            ]
            for key in timing_keys:
                if config.has_option('Timing', key):
                    timing = config.get('Timing', key)
                    is_valid, error = ConfigValidator.validate_timing_range(timing)
                    if not is_valid:
                        errors.append(f"Timing.{key}: {error}")
        
        return len(errors) == 0, errors
```

## 9. Improve File Operations with Better Error Handling

### File: `bypass_token_limit.py` - Line 182

**Current Code:**
```python
except:
    pass
```

**Improved Code:**
```python
except (OSError, PermissionError) as e:
    logger.warning(f"Failed to remove temporary file {tmp_path}: {e}")
    # Try to remove on next run or manual cleanup
except Exception as e:
    logger.error(f"Unexpected error cleaning up temporary file: {e}", exc_info=True)
```

## 10. Add Retry Logic with Exponential Backoff

### Create: `core/retry.py`

```python
"""Retry utilities with exponential backoff"""
import time
import logging
from typing import Callable, TypeVar, Optional, List
from functools import wraps

T = TypeVar('T')
logger = logging.getLogger(__name__)

def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        time.sleep(min(delay, max_delay))
                        delay *= exponential_base
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )
            
            raise last_exception
        return wrapper
    return decorator

# Usage example:
@retry_with_backoff(max_attempts=3, exceptions=(requests.RequestException,))
def fetch_url(url: str) -> requests.Response:
    return requests.get(url, timeout=10)
```

## 11. Add Progress Indicators

### Create: `core/progress.py`

```python
"""Progress indicator utilities"""
from typing import Optional
import sys

class ProgressBar:
    """Simple progress bar for long operations"""
    
    def __init__(self, total: int, description: str = "Progress"):
        self.total = total
        self.current = 0
        self.description = description
        self.bar_length = 50
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current = min(self.current + increment, self.total)
        self._display()
    
    def _display(self):
        """Display progress bar"""
        percent = (self.current / self.total) * 100
        filled = int(self.bar_length * self.current / self.total)
        bar = '=' * filled + '-' * (self.bar_length - filled)
        sys.stdout.write(f'\r{self.description}: [{bar}] {percent:.1f}% ({self.current}/{self.total})')
        sys.stdout.flush()
    
    def finish(self):
        """Finish progress bar"""
        self.current = self.total
        self._display()
        print()  # New line after completion

# Usage:
progress = ProgressBar(total=100, description="Processing files")
for i in range(100):
    # Do work
    progress.update(1)
progress.finish()
```

## Summary

These improvements address:
1. ✅ Bare exception handlers → Specific exception handling
2. ✅ Security issues → Cryptographically secure password generation
3. ✅ Error handling → Custom exceptions and proper logging
4. ✅ Code quality → Type hints and validation
5. ✅ User experience → Progress indicators and better error messages

All improvements maintain backward compatibility and can be implemented incrementally.

