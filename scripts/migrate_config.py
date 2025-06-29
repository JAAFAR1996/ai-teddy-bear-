#!/usr/bin/env python
"""
Script to migrate old configuration format to new format
"""
import json
import os
from pathlib import Path


def migrate_config():
    """Migrate old config format to new format"""
    config_dir = Path(__file__).parent.parent / 'config'
    
    # Map old configs to environment variables
    old_configs = {
        'config.json': {
            'OPENAI_API_KEY': lambda c: c.get('ai', {}).get('openai_api_key'),
            'AZURE_SPEECH_KEY': lambda c: c.get('speech', {}).get('azure_key'),
            'AZURE_SPEECH_REGION': lambda c: c.get('speech', {}).get('azure_region'),
            'DATABASE_URL': lambda c: f"sqlite:///{c.get('database', {}).get('path', 'data/teddy.db')}",
            'LOG_LEVEL': lambda c: c.get('logging', {}).get('level'),
            'JWT_SECRET_KEY': lambda c: c.get('security', {}).get('jwt_secret'),
        }
    }
    
    env_vars = []
    
    for config_file, mappings in old_configs.items():
        config_path = config_dir / config_file
        if config_path.exists():
            with open(config_path, 'r') as f:
                old_config = json.load(f)
            
            for env_var, extractor in mappings.items():
                value = extractor(old_config)
                if value:
                    env_vars.append(f"{env_var}={value}")
    
    # Write to .env file
    env_file = config_dir.parent / '.env'
    existing_vars = []
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            existing_vars = f.readlines()
    
    # Merge with existing
    with open(env_file, 'w') as f:
        # Write existing vars
        for line in existing_vars:
            if not any(line.startswith(var.split('=')[0]) for var in env_vars):
                f.write(line)
        
        # Write new vars
        f.write("\n# Migrated from old config\n")
        for var in env_vars:
            f.write(f"{var}\n")
    
    print(f" Configuration migrated to {env_file}")
    print(" You can now delete old config files:")
    print("   - config/config.json")
    print("   - config/production_config.json")
    print("   - config/staging_config.json")


if __name__ == "__main__":
    migrate_config()