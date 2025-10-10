import unittest
from src.generator.blender_pipeline import BlenderPipeline

class TestBlenderPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = BlenderPipeline()

    def test_generate_model(self):
        description = "A simple cube"
        model_path = self.pipeline.generate_model(description)
        self.assertIsNotNone(model_path)
        self.assertIsInstance(model_path, str)
        self.assertTrue(model_path.endswith('.stl'))  # Assuming STL export

    def test_export_to_cad(self):
        description = "A simple cube"
        model = self.pipeline.generate_model(description)
        cad_file = self.pipeline.export_to_cad(model)
        self.assertTrue(cad_file.endswith('.step'))  # Assuming STEP format for CAD export

if __name__ == '__main__':
    unittest.main()