"""
Data models module for the Spring Test App.
Contains classes for chat messages and other data structures.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class ChatMessage:
    """Represents a single chat message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the chat message to a dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create a ChatMessage instance from a dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
        )


@dataclass
class TestSequence:
    """Represents a generated test sequence with metadata."""
    rows: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the test sequence to a dictionary."""
        return {
            "rows": self.rows,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "name": self.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSequence':
        """Create a TestSequence instance from a dictionary."""
        return cls(
            rows=data["rows"],
            parameters=data["parameters"],
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            name=data.get("name")
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the test sequence to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TestSequence':
        """Create a TestSequence instance from a JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class AppSettings:
    """Application settings that can be saved and loaded."""
    api_key: str = ""
    dark_mode: bool = False
    default_export_format: str = "CSV"
    recent_sequences: List[str] = field(default_factory=list)
    max_chat_history: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the settings to a dictionary."""
        return {
            "api_key": self.api_key,
            "dark_mode": self.dark_mode,
            "default_export_format": self.default_export_format,
            "recent_sequences": self.recent_sequences,
            "max_chat_history": self.max_chat_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Create an AppSettings instance from a dictionary."""
        return cls(
            api_key=data.get("api_key", ""),
            dark_mode=data.get("dark_mode", False),
            default_export_format=data.get("default_export_format", "CSV"),
            recent_sequences=data.get("recent_sequences", []),
            max_chat_history=data.get("max_chat_history", 100)
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the settings to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AppSettings':
        """Create an AppSettings instance from a JSON string."""
        return cls.from_dict(json.loads(json_str)) 