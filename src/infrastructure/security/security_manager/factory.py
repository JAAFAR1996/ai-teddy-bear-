"""
Factory and configuration functions for the security manager.
"""
from typing import Optional

from .manager import EnterpriseSecurityManager

_security_manager: Optional[EnterpriseSecurityManager] = None


def get_security_manager(settings: Optional[object] = None) -> EnterpriseSecurityManager:
    """
    Factory function to create and return a singleton instance of the
    EnterpriseSecurityManager.
    """
    global _security_manager
    if _security_manager is None:
        _security_manager = EnterpriseSecurityManager(settings=settings)
    return _security_manager


def set_security_manager(manager: EnterpriseSecurityManager):
    """
    Explicitly sets the global security manager instance. Useful for testing
    or custom initialization.
    """
    global _security_manager
    _security_manager = manager
