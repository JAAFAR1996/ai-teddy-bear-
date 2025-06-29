# AI Teddy Bear Configuration

## Overview
This directory contains configuration files for different deployment environments of the AI Teddy Bear application.

## Configuration Files

### 1. `default_schema.json`
- JSON schema for validating configuration files
- Defines structure and constraints for configuration

### 2. `default_config.json`
- Default configuration for development environment
- Lowest safety and logging levels
- Ideal for local development and testing

### 3. `staging_config.json`
- Configuration for staging environment
- Intermediate safety and logging levels
- Used for pre-production testing
- Includes experimental feature flags

### 4. `production_config.json`
- Configuration for production environment
- Highest safety and logging levels
- Minimal logging, maximum security

## Configuration Management

### Environment Variables
- Sensitive information should be set via environment variables
- Use `.env` file for local development
- Use secure secret management in production

### Safety Levels
- 0: Minimal filtering
- 1: Basic filtering
- 2: Moderate filtering (default)
- 3: Strict filtering

### Compliance
- COPPA and GDPR compliance settings
- Age restrictions
- Data retention policies

## Best Practices

1. Never commit sensitive information directly to configs
2. Use environment-specific configurations
3. Rotate API keys and secrets regularly
4. Implement least-privilege access

## Validation
- Use `scripts/config_manager.py` to validate and manage configurations
- Configurations are validated against `default_schema.json`

## Deployment
- Different configs used based on `DEPLOYMENT_ENV` environment variable
- Supports: development, staging, production

## Feature Flags
- Experimental features can be enabled/disabled via configuration
- Allows for gradual rollout of new functionality
- Provides flexibility in testing and deployment

## Monitoring and Logging
- Configurable logging levels
- Metrics endpoints for different environments
- Alert configurations for monitoring

## Security Considerations
- Minimal logging in production
- Strict safety filtering
- Comprehensive privacy controls

## Customization
- Easily extend or modify configuration schema
- Add new environment-specific settings
- Implement custom validation rules

## Tools
- Use `scripts/config_manager.py` for:
  - Loading configurations
  - Validating configurations
  - Merging configurations
  - Saving configurations

## Example Usage

```python
from scripts.config_manager import ConfigurationManager

# Load configuration
config_manager = ConfigurationManager()
config = config_manager.load_config('production')

# Validate configuration
is_valid = config_manager.validate_config(config)

# Merge configurations
base_config = config_manager.load_config('default')
merged_config = config_manager.merge_configs(base_config, config)
```

## Contributing
- When adding new configuration options, update `default_schema.json`
- Ensure backward compatibility
- Document new configuration settings
