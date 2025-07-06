"""
Custom exceptions for the plugin system.
"""


class PluginError(Exception):
    """Base class for all plugin-related errors."""
    pass


class SecurityError(PluginError):
    """Raised for security violations, such as a plugin attempting an unauthorized action."""
    pass


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load, for reasons like a missing entry point or import errors."""
    pass


class PluginValidationError(PluginError):
    """Raised when a plugin's manifest or structure is invalid or fails validation."""
    pass


class PluginExecutionError(PluginError):
    """Raised when a plugin encounters an error during its execution."""
    pass
