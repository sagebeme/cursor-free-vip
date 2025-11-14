"""Configuration validation utilities"""
from configparser import ConfigParser
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from .exceptions import ConfigError


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
        errors: List[str] = []
        
        # Validate browser paths
        if config.has_section('Browser'):
            browsers = ['chrome', 'edge', 'firefox', 'brave', 'opera', 'operagx']
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
                'input_wait', 'submit_wait', 'verification_code_input',
                'verification_success_wait', 'verification_retry_wait',
                'email_check_initial_wait', 'email_refresh_wait',
                'settings_page_load_wait', 'failed_retry_time',
                'retry_interval', 'max_timeout'
            ]
            for key in timing_keys:
                if config.has_option('Timing', key):
                    timing = config.get('Timing', key)
                    is_valid, error = ConfigValidator.validate_timing_range(timing)
                    if not is_valid:
                        errors.append(f"Timing.{key}: {error}")
        
        # Validate OAuth settings
        if config.has_section('OAuth'):
            if config.has_option('OAuth', 'timeout'):
                try:
                    timeout = int(config.get('OAuth', 'timeout'))
                    if timeout < 1:
                        errors.append("OAuth.timeout: Must be at least 1 second")
                except ValueError:
                    errors.append("OAuth.timeout: Must be a valid integer")
            
            if config.has_option('OAuth', 'max_attempts'):
                try:
                    max_attempts = int(config.get('OAuth', 'max_attempts'))
                    if max_attempts < 1:
                        errors.append("OAuth.max_attempts: Must be at least 1")
                except ValueError:
                    errors.append("OAuth.max_attempts: Must be a valid integer")
        
        return len(errors) == 0, errors

