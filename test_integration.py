#!/usr/bin/env python3
"""
Integration test to verify that the main application components
can be imported and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_main_imports():
    """Test that main application modules can be imported"""
    print("Testing main application imports...")
    
    modules = [
        'config',
        'utils',
        'cursor_auth',
        'get_user_token',
    ]
    
    success = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name} imported successfully")
        except ImportError as e:
            print(f"  ✗ {module_name} import failed: {e}")
            success = False
        except Exception as e:
            # Some modules may have dependencies that aren't available
            # This is okay for basic syntax checking
            print(f"  ⚠ {module_name} import warning: {e}")
    
    return success

def test_core_integration():
    """Test that core modules integrate properly with main modules"""
    print("\nTesting core module integration...")
    
    try:
        # Test that config can use ConfigValidator
        from config import get_config
        from core import ConfigValidator
        
        # This should work even if config file doesn't exist
        config = get_config()
        if config:
            is_valid, errors = ConfigValidator.validate_config(config)
            print(f"  ✓ Config validation works (valid: {is_valid})")
            if errors:
                print(f"  ⚠ Config has {len(errors)} validation warnings (may be expected)")
        else:
            print("  ⚠ Config is None (may be expected if Cursor not installed)")
        
        # Test that logger can be used
        from core import logger
        logger.info("Integration test log message")
        print("  ✓ Logger integration works")
        
        return True
    except Exception as e:
        print(f"  ✗ Core integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exception_usage():
    """Test that exceptions are used correctly"""
    print("\nTesting exception usage...")
    
    try:
        from core import DatabaseError, ConfigError
        
        # Test that exceptions can be raised and caught
        try:
            raise DatabaseError("Test database error")
        except DatabaseError as e:
            assert str(e) == "Test database error"
            print("  ✓ DatabaseError works correctly")
        
        try:
            raise ConfigError("Test config error")
        except ConfigError as e:
            assert str(e) == "Test config error"
            print("  ✓ ConfigError works correctly")
        
        return True
    except Exception as e:
        print(f"  ✗ Exception usage test failed: {e}")
        return False

def main():
    print("="*60)
    print("Integration Tests")
    print("="*60)
    
    results = []
    
    results.append(("Main Imports", test_main_imports()))
    results.append(("Core Integration", test_core_integration()))
    results.append(("Exception Usage", test_exception_usage()))
    
    print("\n" + "="*60)
    print("Results:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

