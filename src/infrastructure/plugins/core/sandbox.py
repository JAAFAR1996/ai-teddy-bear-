"""
Plugin sandbox for security isolation and resource management.
"""
import logging
from typing import Any, Dict, List, Set

from .enums import PluginPermission
from .exceptions import SecurityError

logger = logging.getLogger(__name__)


class PluginSandbox:
    """
    Provides a secure sandbox for running plugins with isolated permissions,
    resource limits, and restricted access to modules and functions.
    """

    def __init__(self, plugin_name: str, permissions: List[PluginPermission]):
        self.plugin_name = plugin_name
        self.permissions = set(permissions)
        self.allowed_modules = self._get_allowed_modules()
        self.allowed_functions = self._get_allowed_functions()
        self.resource_limits = self._get_resource_limits()
        self._original_import = __builtins__.get("__import__")

        if not self._original_import:
            logger.warning(
                "Could not capture original __import__; import sandboxing will not work.")

    def _get_allowed_modules(self) -> Set[str]:
        """Determines the set of allowed modules based on the plugin's permissions."""
        base_modules = {
            "os", "sys", "json", "datetime", "logging", "asyncio",
            "typing", "pathlib", "tempfile", "uuid", "random", "math"
        }
        permission_map = {
            PluginPermission.BASIC: {"requests", "aiohttp", "pydantic"},
            PluginPermission.ELEVATED: {"redis", "sqlalchemy", "pandas"},
            PluginPermission.ADMIN: {"docker", "kubernetes", "boto3"},
        }
        for perm in self.permissions:
            base_modules.update(permission_map.get(perm, set()))
        return base_modules

    def _get_allowed_functions(self) -> Set[str]:
        """Determines the set of allowed built-in functions based on permissions."""
        base_functions = {
            "print", "len", "str", "int", "float", "bool", "list", "dict", "set",
            "tuple", "max", "min", "sum", "abs", "round", "sorted", "reversed",
            "isinstance", "hasattr", "getattr", "setattr"
        }
        if PluginPermission.BASIC in self.permissions:
            # Note: file system access is a significant permission.
            base_functions.add("open")
        return base_functions

    def _get_resource_limits(self) -> Dict[str, Any]:
        """Defines resource limits for the plugin based on its permissions."""
        limits = {
            "max_execution_time": 30,  # seconds
            "max_memory_mb": 128,
            "max_cpu_percent": 10,
            "max_network_requests": 20,
            "max_file_size_mb": 5,
        }
        if PluginPermission.ELEVATED in self.permissions:
            limits.update({
                "max_execution_time": 300,
                "max_memory_mb": 512,
                "max_cpu_percent": 25,
                "max_network_requests": 100,
                "max_file_size_mb": 50,
            })
        if PluginPermission.ADMIN in self.permissions:
            limits.update({
                "max_execution_time": -1,  # Unlimited
                "max_memory_mb": -1,
                "max_cpu_percent": -1,
                "max_network_requests": -1,
                "max_file_size_mb": -1,
            })
        return limits

    def secure_import(self, name: str, *args, **kwargs):
        """A secure replacement for the __import__ function to restrict module access."""
        if self._original_import is None:
            raise SecurityError("Import sandboxing is not available.")
        if name not in self.allowed_modules:
            raise SecurityError(
                f"Module '{name}' is not allowed for plugin '{self.plugin_name}'.")
        return self._original_import(name, *args, **kwargs)

    def secure_exec(self, code: str, globals_dict: Dict[str, Any], locals_dict: Dict[str, Any] = None):
        """Executes code in a sandboxed environment with restricted built-ins."""
        # A simple static check for obviously dangerous keywords.
        # A more robust solution might involve parsing the AST.
        dangerous_keywords = ["eval", "exec", "subprocess", "ctypes"]
        for keyword in dangerous_keywords:
            if keyword in code:
                raise SecurityError(
                    f"Use of dangerous keyword '{keyword}' is forbidden.")

        restricted_builtins = {
            name: func for name, func in __builtins__.items() if name in self.allowed_functions
        }
        restricted_builtins["__import__"] = self.secure_import

        final_globals = {"__builtins__": restricted_builtins}
        final_globals.update(globals_dict)

        try:
            exec(code, final_globals, locals_dict)
        except Exception as e:
            logger.error(
                f"Error executing sandboxed code for plugin {self.plugin_name}: {e}", exc_info=True)
            raise SecurityError(f"Execution failed in sandbox: {e}") from e
