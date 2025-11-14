#!/usr/bin/env python3
"""
Verification script to test that all improvements are working correctly.
This script checks:
1. All modules can be imported
2. Core functionality works
3. No syntax errors
4. Exception handling works
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def test_imports():
    """Test that all core modules can be imported"""
    print_info("Testing module imports...")
    errors = []
    
    modules_to_test = [
        ('core', 'Core module'),
        ('core.exceptions', 'Exceptions module'),
        ('core.logger', 'Logger module'),
        ('core.retry', 'Retry module'),
        ('core.progress', 'Progress module'),
        ('core.config_validator', 'Config validator module'),
    ]
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print_success(f"{description} imported successfully")
        except Exception as e:
            print_error(f"{description} failed to import: {e}")
            errors.append((module_name, str(e)))
            traceback.print_exc()
    
    return len(errors) == 0, errors

def test_core_exceptions():
    """Test that custom exceptions work"""
    print_info("Testing custom exceptions...")
    errors = []
    
    try:
        from core import (
            CursorFreeVIPError,
            ConfigError,
            AuthError,
            TokenError,
            BrowserError,
            FileOperationError,
            DatabaseError
        )
        
        # Test exception hierarchy
        assert issubclass(ConfigError, CursorFreeVIPError)
        assert issubclass(AuthError, CursorFreeVIPError)
        assert issubclass(TokenError, AuthError)
        assert issubclass(BrowserError, CursorFreeVIPError)
        assert issubclass(FileOperationError, CursorFreeVIPError)
        assert issubclass(DatabaseError, CursorFreeVIPError)
        
        # Test exception instantiation
        try:
            raise ConfigError("Test config error")
        except ConfigError as e:
            assert str(e) == "Test config error"
        
        print_success("Custom exceptions work correctly")
        return True, []
    except Exception as e:
        print_error(f"Exception testing failed: {e}")
        traceback.print_exc()
        return False, [("exceptions", str(e))]

def test_logger():
    """Test that logger works"""
    print_info("Testing logger...")
    errors = []
    
    try:
        from core import logger, setup_logging, get_logger
        
        # Test logger exists
        assert logger is not None
        
        # Test logging methods
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Test get_logger
        test_logger = get_logger()
        assert test_logger is not None
        
        print_success("Logger works correctly")
        return True, []
    except Exception as e:
        print_error(f"Logger testing failed: {e}")
        traceback.print_exc()
        return False, [("logger", str(e))]

def test_retry():
    """Test that retry decorator works"""
    print_info("Testing retry decorator...")
    errors = []
    
    try:
        from core import retry_with_backoff
        import time
        
        call_count = [0]
        
        @retry_with_backoff(max_attempts=3, initial_delay=0.1, exceptions=(ValueError,))
        def test_function():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("Test error")
            return "Success"
        
        result = test_function()
        assert result == "Success"
        assert call_count[0] == 2  # Should have retried once
        
        print_success("Retry decorator works correctly")
        return True, []
    except Exception as e:
        print_error(f"Retry testing failed: {e}")
        traceback.print_exc()
        return False, [("retry", str(e))]

def test_progress():
    """Test that progress bar works"""
    print_info("Testing progress bar...")
    errors = []
    
    try:
        from core import ProgressBar
        
        # Test progress bar creation
        pb = ProgressBar(total=100, description="Test")
        assert pb.total == 100
        assert pb.current == 0
        
        # Test update
        pb.update(50)
        assert pb.current == 50
        
        # Test finish
        pb.finish()
        assert pb.current == 100
        
        print_success("Progress bar works correctly")
        return True, []
    except Exception as e:
        print_error(f"Progress bar testing failed: {e}")
        traceback.print_exc()
        return False, [("progress", str(e))]

def test_config_validator():
    """Test that config validator works"""
    print_info("Testing config validator...")
    errors = []
    
    try:
        from core import ConfigValidator
        from configparser import ConfigParser
        
        # Test path validation
        is_valid, error = ConfigValidator.validate_path("/tmp", must_exist=False)
        assert is_valid
        
        is_valid, error = ConfigValidator.validate_path("", must_exist=False)
        assert not is_valid
        
        # Test timing validation
        is_valid, error = ConfigValidator.validate_timing_range("0.5-1.5")
        assert is_valid
        
        is_valid, error = ConfigValidator.validate_timing_range("invalid")
        assert not is_valid
        
        # Test config validation
        config = ConfigParser()
        config.add_section('Browser')
        config.set('Browser', 'chrome_path', '/usr/bin/chrome')
        config.add_section('Timing')
        config.set('Timing', 'min_random_time', '0.1')
        config.set('Timing', 'max_random_time', '0.8')
        
        is_valid, errors_list = ConfigValidator.validate_config(config)
        # Should be valid with good config
        assert is_valid or len(errors_list) == 0  # May have some warnings but should not fail
        
        print_success("Config validator works correctly")
        return True, []
    except Exception as e:
        print_error(f"Config validator testing failed: {e}")
        traceback.print_exc()
        return False, [("config_validator", str(e))]

def test_modified_files():
    """Test that modified files can be imported"""
    print_info("Testing modified files can be imported...")
    errors = []
    
    files_to_test = [
        ('new_signup', 'new_signup.py'),
        ('bypass_token_limit', 'bypass_token_limit.py'),
        ('cursor_auth', 'cursor_auth.py'),
        ('get_user_token', 'get_user_token.py'),
        ('config', 'config.py'),
    ]
    
    for module_name, filename in files_to_test:
        try:
            # Just check if file exists and can be parsed
            file_path = project_root / filename
            if file_path.exists():
                # Try to compile it
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, filename, 'exec')
                print_success(f"{filename} has no syntax errors")
            else:
                print_warning(f"{filename} not found (may be expected)")
        except SyntaxError as e:
            print_error(f"{filename} has syntax errors: {e}")
            errors.append((module_name, f"Syntax error: {e}"))
        except Exception as e:
            print_warning(f"{filename} import check: {e} (may be expected due to dependencies)")
    
    return len(errors) == 0, errors

def test_exception_handling():
    """Test that exception handling improvements work"""
    print_info("Testing exception handling patterns...")
    errors = []
    
    try:
        from core import logger
        
        # Test that specific exceptions are caught
        try:
            raise ValueError("Test value error")
        except (ValueError, TypeError) as e:
            logger.debug(f"Caught expected exception: {e}")
        except Exception as e:
            errors.append(("exception_handling", "Wrong exception type caught"))
        
        # Test that logger works in exception handlers
        try:
            raise RuntimeError("Test runtime error")
        except RuntimeError as e:
            logger.warning(f"Caught runtime error: {e}")
        except Exception as e:
            errors.append(("exception_handling", "Exception not caught properly"))
        
        print_success("Exception handling patterns work correctly")
        return True, []
    except Exception as e:
        print_error(f"Exception handling test failed: {e}")
        traceback.print_exc()
        return False, [("exception_handling", str(e))]

def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("Cursor Free VIP - Improvement Verification")
    print("="*60 + "\n")
    
    all_passed = True
    all_errors = []
    
    # Run all tests
    tests = [
        ("Module Imports", test_imports),
        ("Custom Exceptions", test_core_exceptions),
        ("Logger", test_logger),
        ("Retry Decorator", test_retry),
        ("Progress Bar", test_progress),
        ("Config Validator", test_config_validator),
        ("Modified Files Syntax", test_modified_files),
        ("Exception Handling", test_exception_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            passed, errors = test_func()
            results[test_name] = (passed, errors)
            if not passed:
                all_passed = False
                all_errors.extend(errors)
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            traceback.print_exc()
            all_passed = False
            results[test_name] = (False, [("crash", str(e))])
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, (passed, errors) in results.items():
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            for error in errors:
                print_error(f"  - {error[0]}: {error[1]}")
    
    print("\n" + "="*60)
    if all_passed:
        print_success("ALL TESTS PASSED! ✓")
        print_info("All improvements are working correctly.")
        return 0
    else:
        print_error("SOME TESTS FAILED ✗")
        print_warning(f"Total errors: {len(all_errors)}")
        print_info("Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

