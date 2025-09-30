import json
import os
import glob
from typing import Dict, List, Optional, Any
from datetime import datetime

class ConfigManager:
    """Manages multiple configuration files for the Discord bot"""
    
    def __init__(self, config_dir: str = ".", default_config_name: str = "config.json"):
        self.config_dir = config_dir
        self.default_config_name = default_config_name
        self.current_config = None
        self.current_config_name = None
        
    def discover_config_files(self) -> List[str]:
        """Discover all JSON config files in the config directory"""
        try:
            # Look for all .json files in the config directory
            pattern = os.path.join(self.config_dir, "*.json")
            config_files = glob.glob(pattern)
            
            # Filter out non-config files and sort by name
            valid_configs = []
            for file_path in config_files:
                filename = os.path.basename(file_path)
                # Skip files that don't look like configs
                if not filename.startswith('.') and filename != 'package.json':
                    valid_configs.append(file_path)
            
            return sorted(valid_configs)
        except Exception as e:
            print(f"Error discovering config files: {e}")
            return []
    
    def get_config_names(self) -> List[str]:
        """Get list of available config file names (without path)"""
        config_files = self.discover_config_files()
        return [os.path.basename(f) for f in config_files]
    
    def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate that a config has all required fields"""
        required_fields = ["token", "keywords", "case_sensitive", "respond_to_self", 
                          "reply_to_message", "role_mentions", "allowed_channels", 
                          "message_delay_minutes"]
        
        missing_fields = []
        for field in required_fields:
            if field not in config_data:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate token
        if not config_data.get("token") or config_data["token"] == "YOUR_USER_TOKEN_HERE":
            return False, "Invalid or missing Discord token"
        
        # Validate keywords is a dict
        if not isinstance(config_data.get("keywords"), dict):
            return False, "Keywords must be a dictionary"
        
        # Validate role_mentions is a dict
        if not isinstance(config_data.get("role_mentions"), dict):
            return False, "Role mentions must be a dictionary"
        
        # Validate allowed_channels is a list
        if not isinstance(config_data.get("allowed_channels"), list):
            return False, "Allowed channels must be a list"
        
        # Validate numeric fields
        try:
            delay = int(config_data.get("message_delay_minutes", 0))
            if delay < 0:
                return False, "Message delay must be non-negative"
        except (ValueError, TypeError):
            return False, "Message delay must be a valid number"
        
        return True, "Config is valid"
    
    def load_config(self, config_name: str = None) -> tuple[Optional[Dict[str, Any]], str]:
        """Load configuration from a specific file or default"""
        if config_name is None:
            config_name = self.default_config_name
        
        config_path = os.path.join(self.config_dir, config_name)
        
        try:
            if not os.path.exists(config_path):
                return None, f"Config file '{config_name}' not found"
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validate the config
            is_valid, validation_msg = self.validate_config(config_data)
            if not is_valid:
                return None, f"Invalid config: {validation_msg}"
            
            self.current_config = config_data
            self.current_config_name = config_name
            return config_data, "Config loaded successfully"
            
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON in config file: {e}"
        except Exception as e:
            return None, f"Error loading config: {e}"
    
    def save_config(self, config_data: Dict[str, Any], config_name: str = None) -> tuple[bool, str]:
        """Save configuration to a specific file or current file"""
        if config_name is None:
            config_name = self.current_config_name or self.default_config_name
        
        config_path = os.path.join(self.config_dir, config_name)
        
        try:
            # Validate before saving
            is_valid, validation_msg = self.validate_config(config_data)
            if not is_valid:
                return False, f"Cannot save invalid config: {validation_msg}"
            
            # Create backup if file exists
            if os.path.exists(config_path):
                backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    os.rename(config_path, backup_path)
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")
            
            # Save the config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            self.current_config = config_data
            self.current_config_name = config_name
            return True, "Config saved successfully"
            
        except Exception as e:
            return False, f"Error saving config: {e}"
    
    def create_config(self, config_name: str, template_data: Dict[str, Any] = None) -> tuple[bool, str]:
        """Create a new configuration file"""
        if not config_name.endswith('.json'):
            config_name += '.json'
        
        config_path = os.path.join(self.config_dir, config_name)
        
        if os.path.exists(config_path):
            return False, f"Config file '{config_name}' already exists"
        
        # Use template data or create default
        if template_data is None:
            template_data = self.get_default_config()
        
        return self.save_config(template_data, config_name)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration template"""
        return {
            "token": "YOUR_USER_TOKEN_HERE",
            "keywords": {
                "hello": "Hi there! How can I help you?",
                "help": "I'm here to assist you!",
                "test": "This is an automated response!"
            },
            "case_sensitive": False,
            "respond_to_self": False,
            "reply_to_message": True,
            "role_mentions": {},
            "allowed_channels": [],
            "message_delay_minutes": 5
        }
    
    def copy_config(self, source_name: str, target_name: str) -> tuple[bool, str]:
        """Copy an existing config to a new name"""
        if not target_name.endswith('.json'):
            target_name += '.json'
        
        source_path = os.path.join(self.config_dir, source_name)
        target_path = os.path.join(self.config_dir, target_name)
        
        if not os.path.exists(source_path):
            return False, f"Source config '{source_name}' not found"
        
        if os.path.exists(target_path):
            return False, f"Target config '{target_name}' already exists"
        
        try:
            # Load source config
            with open(source_path, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            
            # Save as new config
            return self.save_config(source_data, target_name)
            
        except Exception as e:
            return False, f"Error copying config: {e}"
    
    def delete_config(self, config_name: str) -> tuple[bool, str]:
        """Delete a configuration file"""
        config_path = os.path.join(self.config_dir, config_name)
        
        if not os.path.exists(config_path):
            return False, f"Config file '{config_name}' not found"
        
        # Don't allow deleting the default config
        if config_name == self.default_config_name:
            return False, "Cannot delete the default config file"
        
        try:
            os.remove(config_path)
            
            # If we're deleting the current config, reset to default
            if self.current_config_name == config_name:
                self.current_config_name = None
                self.current_config = None
            
            return True, f"Config '{config_name}' deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting config: {e}"
    
    def get_current_config(self) -> Optional[Dict[str, Any]]:
        """Get the currently loaded configuration"""
        return self.current_config
    
    def get_current_config_name(self) -> Optional[str]:
        """Get the name of the currently loaded configuration"""
        return self.current_config_name
    
    def reload_current_config(self) -> tuple[Optional[Dict[str, Any]], str]:
        """Reload the currently loaded configuration"""
        if self.current_config_name:
            return self.load_config(self.current_config_name)
        else:
            return self.load_config()  # Load default
