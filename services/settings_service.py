"""
Settings service for the Spring Test App.
Contains functions for saving and loading application settings.
"""
import os
import json
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Default settings
DEFAULT_SETTINGS = {
    "api_key": "",
    "default_export_format": "CSV",
    "recent_sequences": [],
    "max_chat_history": 100
}

# App salt for encryption (do not change)
APP_SALT = b'SpringTestApp_2025_Salt_Value'
# App encryption key derivation password
APP_PASSWORD = b'SpringTestApp_Secure_Password_2025'

class SettingsService:
    """Service for managing application settings."""
    
    def __init__(self):
        """Initialize the settings service."""
        self.settings = DEFAULT_SETTINGS.copy()
        self.settings_dir = self._ensure_data_dir()
        self.settings_file = os.path.join(self.settings_dir, "settings.dat")
        self.encryption_key = self._generate_key()
        self.load_settings()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists.
        
        Returns:
            Path to the data directory.
        """
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "appdata")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            # Create .gitignore to prevent accidental commit of sensitive data
            with open(os.path.join(data_dir, ".gitignore"), "w") as f:
                f.write("# Ignore all files in this directory\n*\n!.gitignore\n")
        return data_dir
    
    def _generate_key(self):
        """Generate encryption key from app password.
        
        Returns:
            Encryption key.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=APP_SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(APP_PASSWORD))
        return key
    
    def load_settings(self):
        """Load settings from file."""
        if not os.path.exists(self.settings_file):
            logging.info("Settings file not found, using defaults")
            return
        
        try:
            # Read encrypted data
            with open(self.settings_file, "rb") as f:
                encrypted_data = f.read()
            
            # Decrypt data
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Parse JSON
            loaded_settings = json.loads(decrypted_data.decode('utf-8'))
            
            # Update settings with loaded values
            self.settings.update(loaded_settings)
            logging.info("Settings loaded successfully")
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            # Convert settings to JSON
            settings_json = json.dumps(self.settings, indent=2)
            
            # Encrypt data
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(settings_json.encode('utf-8'))
            
            # Write encrypted data
            with open(self.settings_file, "wb") as f:
                f.write(encrypted_data)
            
            logging.info("Settings saved successfully")
        except Exception as e:
            logging.error(f"Error saving settings: {str(e)}")
    
    def get_api_key(self):
        """Get the API key.
        
        Returns:
            The API key.
        """
        return self.settings.get("api_key", "")
    
    def set_api_key(self, api_key):
        """Set the API key.
        
        Args:
            api_key: The API key to set.
        """
        self.settings["api_key"] = api_key
        self.save_settings()
    
    def get_default_export_format(self):
        """Get the default export format.
        
        Returns:
            The default export format.
        """
        return self.settings.get("default_export_format", "CSV")
    
    def set_default_export_format(self, format):
        """Set the default export format.
        
        Args:
            format: The format to use.
        """
        self.settings["default_export_format"] = format
        self.save_settings()
    
    def add_recent_sequence(self, sequence_id):
        """Add a sequence to the recent sequences list.
        
        Args:
            sequence_id: The ID of the sequence to add.
        """
        recent = self.settings.get("recent_sequences", [])
        
        # Remove the sequence if it already exists
        if sequence_id in recent:
            recent.remove(sequence_id)
        
        # Add to the beginning of the list
        recent.insert(0, sequence_id)
        
        # Limit the list to 10 items
        self.settings["recent_sequences"] = recent[:10]
        self.save_settings()
    
    def get_recent_sequences(self):
        """Get the list of recent sequences.
        
        Returns:
            List of recent sequence IDs.
        """
        return self.settings.get("recent_sequences", []) 