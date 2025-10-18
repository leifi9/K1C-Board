"""
Tests for the parametric shapes module.

These tests verify the functionality of parametric shape generation
including gears, springs, and threads.
"""

import unittest
from src.generator.parametric_shapes import (
    ParametricGenerator, 
    GearShape, 
    SpringShape, 
    ThreadShape
)


class TestParametricShapes(unittest.TestCase):
    """Test cases for parametric shape generation."""

    def test_gear_shape_creation(self):
        """Test that GearShape can be created with valid parameters."""
        gear = GearShape(module=1.0, teeth=20, pressure_angle=20.0, thickness=0.5)
        self.assertIsNotNone(gear)
        self.assertEqual(gear.module, 1.0)
        self.assertEqual(gear.teeth, 20)

    def test_gear_mesh_generation(self):
        """Test that GearShape generates mesh data."""
        gear = GearShape(module=1.0, teeth=20, pressure_angle=20.0, thickness=0.5)
        vertices, faces = gear.generate_mesh_data()
        self.assertIsNotNone(vertices)
        self.assertIsNotNone(faces)
        self.assertIsInstance(vertices, list)
        self.assertIsInstance(faces, list)
        self.assertGreater(len(vertices), 0)
        self.assertGreater(len(faces), 0)

    def test_spring_shape_creation(self):
        """Test that SpringShape can be created with valid parameters."""
        spring = SpringShape(coils=5.0, radius=1.0, wire_radius=0.1, pitch=0.3)
        self.assertIsNotNone(spring)
        self.assertEqual(spring.coils, 5.0)
        self.assertEqual(spring.radius, 1.0)

    def test_spring_mesh_generation(self):
        """Test that SpringShape generates mesh data."""
        spring = SpringShape(coils=5.0, radius=1.0, wire_radius=0.1, pitch=0.3)
        vertices, faces = spring.generate_mesh_data()
        self.assertIsNotNone(vertices)
        self.assertIsNotNone(faces)
        self.assertIsInstance(vertices, list)
        self.assertIsInstance(faces, list)
        self.assertGreater(len(vertices), 0)
        self.assertGreater(len(faces), 0)

    def test_thread_shape_creation(self):
        """Test that ThreadShape can be created with valid parameters."""
        thread = ThreadShape(
            major_diameter=1.0, 
            minor_diameter=0.8, 
            pitch=0.2, 
            length=2.0, 
            thread_angle=60.0
        )
        self.assertIsNotNone(thread)
        self.assertEqual(thread.major_diameter, 1.0)
        self.assertEqual(thread.pitch, 0.2)

    def test_thread_mesh_generation(self):
        """Test that ThreadShape generates mesh data."""
        thread = ThreadShape(
            major_diameter=1.0, 
            minor_diameter=0.8, 
            pitch=0.2, 
            length=2.0, 
            thread_angle=60.0
        )
        vertices, faces = thread.generate_mesh_data()
        self.assertIsNotNone(vertices)
        self.assertIsNotNone(faces)
        self.assertIsInstance(vertices, list)
        self.assertIsInstance(faces, list)
        self.assertGreater(len(vertices), 0)

    def test_parametric_generator_gear(self):
        """Test ParametricGenerator creates gear shapes."""
        params = {
            'module': 1.0,
            'teeth': 20,
            'pressure_angle': 20.0,
            'thickness': 0.5
        }
        shape = ParametricGenerator.create_shape('gear', params)
        self.assertIsNotNone(shape)
        self.assertIsInstance(shape, GearShape)

    def test_parametric_generator_spring(self):
        """Test ParametricGenerator creates spring shapes."""
        params = {
            'coils': 5.0,
            'radius': 1.0,
            'wire_radius': 0.1,
            'pitch': 0.3
        }
        shape = ParametricGenerator.create_shape('spring', params)
        self.assertIsNotNone(shape)
        self.assertIsInstance(shape, SpringShape)

    def test_parametric_generator_thread(self):
        """Test ParametricGenerator creates thread shapes."""
        params = {
            'major_diameter': 1.0,
            'minor_diameter': 0.8,
            'pitch': 0.2,
            'length': 2.0,
            'thread_angle': 60.0
        }
        shape = ParametricGenerator.create_shape('thread', params)
        self.assertIsNotNone(shape)
        self.assertIsInstance(shape, ThreadShape)

    def test_parametric_generator_invalid_type(self):
        """Test ParametricGenerator raises error for invalid shape type."""
        params = {}
        with self.assertRaises(ValueError):
            ParametricGenerator.create_shape('invalid_shape', params)


if __name__ == '__main__':
    unittest.main()
