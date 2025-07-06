"""
Factory for creating the RBAC manager instance.
"""
from typing import Optional

from .manager import TeddyBearRBACManager

_rbac_manager: Optional[TeddyBearRBACManager] = None


def get_rbac_manager() -> TeddyBearRBACManager:
    """
    Factory function to create and return a singleton instance of the
    TeddyBearRBACManager.
    """
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = TeddyBearRBACManager()
    return _rbac_manager
