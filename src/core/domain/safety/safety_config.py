"""
Safety Configuration Management for AI Content Filtering
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from .models import SafetyConfig


class SafetyConfigManager:
    """Advanced safety configuration management"""
    
    def __init__(self, config_path: str = "config/safety_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> SafetyConfig:
        """Load safety configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return SafetyConfig(**config_data)
            else:
                # Create default config
                default_config = self._create_default_config()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> SafetyConfig:
        """Create default safety configuration"""
        return SafetyConfig(
            min_child_age=3,
            max_child_age=12,
            toxicity_threshold=0.1,
            high_risk_threshold=0.3,
            critical_threshold=0.7,
            enable_strict_mode=True,
            enable_educational_boost=True,
            use_local_models=False,
            enable_caching=True,
            cache_ttl_seconds=3600,
            notify_parents_on_risk=True,
            log_all_interactions=True,
            max_processing_time_ms=500.0,
            enable_async_processing=True
        )
    
    def _save_config(self, config: SafetyConfig) -> None:
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            config_dict = asdict(config)
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def update_config(self, **kwargs) -> SafetyConfig:
        """Update configuration parameters"""
        config_dict = asdict(self.config)
        config_dict.update(kwargs)
        
        new_config = SafetyConfig(**config_dict)
        if new_config.validate():
            self.config = new_config
            self._save_config(new_config)
            return new_config
        else:
            raise ValueError("Invalid configuration parameters")
    
    def get_age_specific_config(self, child_age: int) -> Dict[str, Any]:
        """Get age-specific safety configuration"""
        base_config = asdict(self.config)
        
        # Age-specific modifications
        if child_age <= 4:
            base_config.update({
                'toxicity_threshold': 0.05,  # More strict for younger children
                'enable_strict_mode': True,
                'notify_parents_on_risk': True
            })
        elif child_age <= 6:
            base_config.update({
                'toxicity_threshold': 0.08,
                'enable_strict_mode': True
            })
        elif child_age <= 8:
            base_config.update({
                'toxicity_threshold': 0.1,
                'enable_strict_mode': False
            })
        else:
            base_config.update({
                'toxicity_threshold': 0.15,
                'enable_strict_mode': False
            })
        
        return base_config
    
    def export_config(self, export_path: str) -> None:
        """Export configuration to specified path"""
        with open(export_path, 'w', encoding='utf-8') as f:
            config_dict = asdict(self.config)
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def import_config(self, import_path: str) -> SafetyConfig:
        """Import configuration from specified path"""
        with open(import_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        new_config = SafetyConfig(**config_data)
        if new_config.validate():
            self.config = new_config
            self._save_config(new_config)
            return new_config
        else:
            raise ValueError("Invalid imported configuration")
    
    def reset_to_defaults(self) -> SafetyConfig:
        """Reset configuration to defaults"""
        self.config = self._create_default_config()
        self._save_config(self.config)
        return self.config
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'version': '1.0.0',
            'last_updated': os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0,
            'toxicity_threshold': self.config.toxicity_threshold,
            'strict_mode': self.config.enable_strict_mode,
            'age_range': f"{self.config.min_child_age}-{self.config.max_child_age}",
            'async_enabled': self.config.enable_async_processing,
            'caching_enabled': self.config.enable_caching
        } 