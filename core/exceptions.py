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

