import os
import logging
import logging.config
import json
import yaml
from typing import Dict, Any, Optional

class LoggingConfigurator:
    """
    Advanced logging configuration utility
    """
    @staticmethod
    def configure_logging(
        log_level: str = 'INFO', 
        log_dir: str = 'logs', 
        config_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Configure logging with flexible options
        
        :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :param log_dir: Directory to store log files
        :param config_path: Path to custom logging configuration
        :return: Logging configuration details
        """
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Default logging configuration
        default_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d - %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': log_level,
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': log_level,
                    'formatter': 'detailed',
                    'filename': os.path.join(log_dir, 'ai_teddy_bear.log'),
                    'maxBytes': 10 * 1024 * 1024,  # 10 MB
                    'backupCount': 5
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'detailed',
                    'filename': os.path.join(log_dir, 'errors.log'),
                    'maxBytes': 5 * 1024 * 1024,  # 5 MB
                    'backupCount': 3
                }
            },
            'loggers': {
                '': {  # Root logger
                    'handlers': ['console', 'file', 'error_file'],
                    'level': log_level,
                    'propagate': True
                },
                'ai_teddy_bear': {
                    'handlers': ['console', 'file', 'error_file'],
                    'level': log_level,
                    'propagate': False
                }
            }
        }

        # Override with custom configuration if provided
        if config_path:
            try:
                if config_path.endswith('.json'):
                    with open(config_path, 'r') as f:
                        custom_config = json.load(f)
                elif config_path.endswith(('.yaml', '.yml')):
                    with open(config_path, 'r') as f:
                        custom_config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config file type: {config_path}")
                
                # Deep merge custom config with default config
                default_config = LoggingConfigurator._deep_merge(default_config, custom_config)
            except Exception as e:
                logging.warning(f"Could not load custom logging config: {e}")

        # Configure logging
        logging.config.dictConfig(default_config)

        return {
            'log_directory': log_dir,
            'log_level': log_level,
            'config_source': config_path or 'default'
        }

    @staticmethod
    def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries
        
        :param base: Base dictionary
        :param update: Dictionary to merge into base
        :return: Merged dictionary
        """
        for key, value in update.items():
            if isinstance(value, dict):
                base[key] = LoggingConfigurator._deep_merge(base.get(key, {}), value)
            else:
                base[key] = value
        return base

    @staticmethod
    def log_system_info():
        """
        Log system and environment information
        """
        logger = logging.getLogger(__name__)
        
        try:
            import platform
            import sys
            
            logger.info("System Information:")
            logger.info(f"Python Version: {platform.python_version()}")
            logger.info(f"Platform: {platform.platform()}")
            logger.info(f"Executable: {sys.executable}")
            logger.info(f"Current Working Directory: {os.getcwd()}")
            
            # Log environment variables (excluding sensitive ones)
            safe_env_vars = [
                'PATH', 'HOME', 'USER', 'LANG', 'LC_ALL', 
                'PYTHON_VERSION', 'DEPLOYMENT_ENV'
            ]
            
            logger.info("Environment Variables:")
            for var in safe_env_vars:
                if var in os.environ:
                    logger.info(f"{var}: {os.environ[var]}")
        
        except Exception as e:
            logger.error(f"Error logging system info: {e}")

def main():
    """
    CLI for logging configuration
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Teddy Bear Logging Configurator')
    parser.add_argument('-l', '--level', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default='INFO', 
                        help='Set logging level')
    parser.add_argument('-d', '--directory', 
                        default='logs', 
                        help='Log file directory')
    parser.add_argument('-c', '--config', 
                        help='Path to custom logging configuration file')
    
    args = parser.parse_args()
    
    # Configure logging
    config_details = LoggingConfigurator.configure_logging(
        log_level=args.level, 
        log_dir=args.directory, 
        config_path=args.config
    )
    
    # Log system information
    LoggingConfigurator.log_system_info()
    
    # Print configuration details
    print(json.dumps(config_details, indent=2))

if __name__ == "__main__":
    main()
