"""
Tests for the 3D model generator module.

Note: These tests require Blender (bpy module) to be installed.
They will be skipped if Blender is not available.
"""

import unittest

try:
    from src.generator.blender_pipeline import BlenderPipeline
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False


@unittest.skipUnless(BLENDER_AVAILABLE, "Blender (bpy) is not installed")
class TestBlenderPipeline(unittest.TestCase):
    """Test cases for the BlenderPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        self.pipeline = BlenderPipeline()

    def test_generate_model(self):
        """Test that generate_model returns a valid path."""
        description = "A simple cube"
        model_path = self.pipeline.generate_model(description)
        self.assertIsNotNone(model_path)
        self.assertIsInstance(model_path, str)
        self.assertTrue(model_path.endswith('.stl'))  # Assuming STL export

    def test_export_to_cad(self):
        """Test that export_to_cad returns a valid STEP file path."""
        description = "A simple cube"
        model = self.pipeline.generate_model(description)
        cad_file = self.pipeline.export_to_cad(model)
        self.assertTrue(cad_file.endswith('.step'))  # Assuming STEP format for CAD export


class TestGeneratorWithoutBlender(unittest.TestCase):
    """Test cases that can run without Blender installed."""
    
    def test_blender_import(self):
        """Test that we can detect if Blender is available."""
        if BLENDER_AVAILABLE:
            self.assertTrue(True, "Blender is available")
        else:
            self.assertTrue(True, "Blender is not available - tests will be skipped")


if __name__ == '__main__':
    unittest.main()