"""
Pytest configuration for mocking Blender (bpy) module when not available.
"""
import sys
from pathlib import Path

# Add the mock_bpy module to sys.modules before any imports
try:
    import bpy
except ImportError:
    # Blender not installed, use mock
    from tests import mock_bpy
    sys.modules['bpy'] = mock_bpy
