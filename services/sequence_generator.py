"""
Sequence generator service for the Spring Test App.
Contains classes and functions for generating test sequences.
"""
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Callable
from utils.api_client import APIClient
from models.data_models import TestSequence
from PyQt5.QtCore import QObject, pyqtSignal


class SequenceGenerator(QObject):
    """Service for generating test sequences."""
    
    # Define signals
    sequence_generated = pyqtSignal(object, str)  # TestSequence, error_message
    progress_updated = pyqtSignal(int)            # Progress percentage (0-100)
    status_updated = pyqtSignal(str)              # Status message
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """Initialize the sequence generator service.
        
        Args:
            api_client: API client to use for generation. If None, create a new one.
        """
        super().__init__()
        self.api_client = api_client or APIClient()
        self.last_parameters = {}
        self.last_sequence = None
        self.history = []
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for the API client.
        
        Args:
            api_key: API key to use.
        """
        self.api_client.set_api_key(api_key)
    
    def generate_sequence(self, parameters: Dict[str, Any]) -> Tuple[Optional[TestSequence], str]:
        """Generate a test sequence based on parameters (synchronous version).
        
        Note: This method is kept for backward compatibility but should be avoided
        in the UI to prevent freezing.
        
        Args:
            parameters: Dictionary of spring parameters.
            
        Returns:
            Tuple of (TestSequence object, error message if any)
        """
        # Save parameters for reference
        self.last_parameters = parameters
        
        # Generate sequence
        df, response_text = self.api_client.generate_sequence(parameters)
        
        # If generation failed, return error
        if df.empty:
            return None, response_text
        
        # Create TestSequence object
        sequence = TestSequence(
            rows=df.to_dict('records'),
            parameters=parameters
        )
        
        # Save sequence for reference
        self.last_sequence = sequence
        
        # Add to history
        self.history.append(sequence)
        if len(self.history) > 10:  # Keep history limited
            self.history = self.history[-10:]
        
        return sequence, ""
    
    def generate_sequence_async(self, parameters: Dict[str, Any]) -> None:
        """Generate a test sequence based on parameters asynchronously.
        
        Args:
            parameters: Dictionary of spring parameters.
        """
        # Save parameters for reference
        self.last_parameters = parameters
        
        # Start async generation
        self.api_client.generate_sequence_async(
            parameters,
            self._on_sequence_generated,
            self.progress_updated.emit,  # Forward progress signal
            self.status_updated.emit     # Forward status signal
        )
    
    def _on_sequence_generated(self, df: pd.DataFrame, error_msg: str) -> None:
        """Handle sequence generation completion.
        
        Args:
            df: Generated DataFrame.
            error_msg: Error message if any.
        """
        sequence = None
        
        if not df.empty:
            # Create TestSequence object
            sequence = TestSequence(
                rows=df.to_dict('records'),
                parameters=self.last_parameters
            )
            
            # Save sequence for reference
            self.last_sequence = sequence
            
            # Add to history
            self.history.append(sequence)
            if len(self.history) > 10:  # Keep history limited
                self.history = self.history[-10:]
        
        # Emit signal
        self.sequence_generated.emit(sequence, error_msg)
    
    def cancel_current_operation(self) -> None:
        """Cancel the current operation."""
        self.api_client.cancel_current_operation()
    
    def get_last_sequence(self) -> Optional[TestSequence]:
        """Get the last generated sequence.
        
        Returns:
            The last generated sequence, or None if none available.
        """
        return self.last_sequence
    
    def get_sequence_history(self) -> List[TestSequence]:
        """Get the sequence generation history.
        
        Returns:
            List of generated sequences.
        """
        return self.history
    
    def add_to_history(self, sequence: TestSequence) -> None:
        """Add a sequence to the history.
        
        Args:
            sequence: Sequence to add.
        """
        self.history.append(sequence)
        if len(self.history) > 10:  # Keep history limited
            self.history = self.history[-10:]
    
    def clear_history(self) -> None:
        """Clear the sequence generation history."""
        self.history = []
    
    def validate_sequence(self, sequence: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a sequence.
        
        Args:
            sequence: Sequence to validate.
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation checks
        if not sequence:
            return False, "Sequence is empty"
        
        required_columns = ["Row", "CMD", "Description", "Condition", "Unit", "Tolerance", "Speed rpm"]
        
        # Check if all required columns are present
        for col in required_columns:
            if col not in sequence[0]:
                return False, f"Missing required column: {col}"
        
        # More validation could be added here
        
        return True, ""
    
    def create_sequence_from_template(self, template_name: str, parameters: Dict[str, Any]) -> Optional[TestSequence]:
        """Create a sequence from a predefined template.
        
        Args:
            template_name: Name of the template to use.
            parameters: Dictionary of parameters to fill in.
            
        Returns:
            Generated sequence, or None if template not found.
        """
        # This would load predefined templates and fill in the parameters
        # For now, just return None
        return None 