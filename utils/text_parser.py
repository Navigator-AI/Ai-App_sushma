"""
Text parser module for the Spring Test App.
Contains functions for extracting spring parameters from natural language text.
"""
import re
from typing import Dict, Any
from datetime import datetime
from utils.constants import PARAMETER_PATTERNS


def extract_parameters(text: str) -> Dict[str, Any]:
    """
    Extract spring parameters from natural language text.
    
    Args:
        text: The natural language text to extract parameters from.
        
    Returns:
        A dictionary of extracted parameters.
    """
    parameters = {}
    
    # Extract test type
    if re.search(r'\b(?:compress|compression)\b', text, re.IGNORECASE):
        parameters["Test Type"] = "Compression"
    elif re.search(r'\b(?:tens|tension|extension|extend)\b', text, re.IGNORECASE):
        parameters["Test Type"] = "Tension"
    else:
        # Default to compression if not specified
        parameters["Test Type"] = "Compression"
    
    # Extract parameters based on patterns
    for param, pattern in PARAMETER_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Convert to float if it's a numeric value
            if param not in ["Part Number", "Model Number", "Customer ID"]:
                try:
                    parameters[param] = float(value)
                except ValueError:
                    parameters[param] = value
            else:
                parameters[param] = value
    
    # Add timestamp to parameters
    parameters["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return parameters


def extract_command_sequence(text: str) -> Dict[str, Any]:
    """
    Extract a command sequence from text (usually API response).
    
    Args:
        text: The text containing a command sequence, often from API response.
        
    Returns:
        A dictionary representation of the command sequence.
    """
    import json
    
    # Try to extract JSON from the response
    json_match = re.search(r'```json\n(.*?)\n```|(\[.*\])', text, re.DOTALL)
    if json_match:
        json_content = json_match.group(1) or json_match.group(2)
    else:
        json_content = text
    
    # Clean up any remaining markdown or text
    json_content = re.sub(r'^```.*|```$', '', json_content, flags=re.MULTILINE).strip()
    
    # Try to parse the JSON
    try:
        data = json.loads(json_content)
        return data
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract just the array part
        array_match = re.search(r'\[(.*)\]', json_content, re.DOTALL)
        if array_match:
            cleaned_json = '[' + array_match.group(1) + ']'
            try:
                data = json.loads(cleaned_json)
                return data
            except json.JSONDecodeError:
                pass
    
    # If all parsing attempts fail, return an empty list
    return []


def format_parameter_text(parameters: Dict[str, Any]) -> str:
    """
    Format parameters for display or for use in API prompts.
    
    Args:
        parameters: Dictionary of parameters.
        
    Returns:
        Formatted parameter text.
    """
    lines = []
    
    # Format each parameter as a line
    for key, value in parameters.items():
        # Skip timestamp and other metadata
        if key in ["Timestamp"]:
            continue
            
        # Format numeric values with appropriate precision
        if isinstance(value, float):
            # Use 1 decimal place for most values, 2 for small values
            if value < 0.1:
                formatted_value = f"{value:.3f}"
            elif value < 1:
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = f"{value:.1f}"
                
            # Add units based on parameter type
            if "Length" in key or "Diameter" in key:
                formatted_value += " mm"
            elif "Force" in key or "Load" in key:
                formatted_value += " N"
            elif "Rate" in key:
                formatted_value += " N/mm"
        else:
            formatted_value = str(value)
            
        lines.append(f"{key}: {formatted_value}")
    
    return "\n".join(lines)


def extract_error_message(response_text: str) -> str:
    """
    Extract error message from API response.
    
    Args:
        response_text: The API response text.
        
    Returns:
        Extracted error message or empty string if none found.
    """
    # Common error patterns
    error_patterns = [
        r'error["\']?\s*:\s*["\']([^"\']+)["\']',  # "error": "message"
        r'message["\']?\s*:\s*["\']([^"\']+)["\']',  # "message": "error message"
        r'ERROR:\s*(.+?)(?:\n|$)',  # ERROR: message
        r'Exception:\s*(.+?)(?:\n|$)',  # Exception: message
    ]
    
    for pattern in error_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "" 