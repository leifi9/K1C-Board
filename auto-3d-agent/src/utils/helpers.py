"""
Utility functions for the Auto 3D Agent.

This module provides helper functions for configuration loading, validation,
logging, and data processing.
"""


def load_config(config_file):
    """
    Load configuration settings from a YAML file.
    
    Args:
        config_file: Path to the YAML configuration file
        
    Returns:
        dict: Configuration settings
    """
    import yaml
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def validate_input(input_data):
    """
    Validate the input data for the agent.
    
    Args:
        input_data: Input data to validate
        
    Returns:
        bool: True if input is valid
        
    Raises:
        ValueError: If input data is empty
    """
    if not input_data:
        raise ValueError("Input data cannot be empty.")
    return True


def log_message(message):
    """
    Log messages for debugging and tracking.
    
    Args:
        message: Message to log
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info(message)


def extract_keywords_from_text(text):
    """
    Simple keyword extraction from text.
    
    Args:
        text: Input text to extract keywords from
        
    Returns:
        list: List of unique keywords
    """
    import re
    keywords = re.findall(r'\b\w+\b', text)
    return list(set(keywords))  # Return unique keywords


def format_output_for_cad(model_data):
    """
    Format the model data for CAD export.
    
    Args:
        model_data: Model data dictionary
        
    Returns:
        dict: Formatted data for CAD export
    """
    return {
        'model_name': model_data.get('name'),
        'dimensions': model_data.get('dimensions'),
        'file_format': 'STEP'
    }