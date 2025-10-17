"""
Parametric shape generation module for creating specialized 3D shapes.

This module provides generators for parametric shapes like gears, springs, and threads.
"""

import math
import numpy as np
from typing import Dict, Any, Tuple, List


class ParametricShape:
    """Base class for parametric shape generation."""
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """
        Generate mesh data (vertices and faces) for the shape.
        
        Returns:
            Tuple of (vertices, faces) where:
                - vertices is a list of (x, y, z) tuples
                - faces is a list of (v1, v2, v3) tuples (triangle indices)
        """
        raise NotImplementedError("Subclasses must implement generate_mesh_data")


class GearShape(ParametricShape):
    """Generate a parametric gear shape."""
    
    def __init__(self, module: float, teeth: int, pressure_angle: float, thickness: float):
        """
        Initialize gear parameters.
        
        Args:
            module: Gear module (size parameter)
            teeth: Number of teeth
            pressure_angle: Pressure angle in degrees
            thickness: Gear thickness
        """
        self.module = module
        self.teeth = teeth
        self.pressure_angle = pressure_angle
        self.thickness = thickness
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate mesh data for a gear."""
        vertices = []
        faces = []
        
        # Calculate gear parameters
        pitch_radius = (self.module * self.teeth) / 2
        addendum = self.module
        dedendum = 1.25 * self.module
        outer_radius = pitch_radius + addendum
        inner_radius = pitch_radius - dedendum
        
        # Generate gear profile
        segments_per_tooth = 8
        total_segments = self.teeth * segments_per_tooth
        
        # Generate top and bottom vertices
        for i in range(total_segments):
            angle = (2 * math.pi * i) / total_segments
            tooth_phase = (i % segments_per_tooth) / segments_per_tooth
            
            # Vary radius to create tooth profile
            if tooth_phase < 0.2:
                radius = inner_radius + (outer_radius - inner_radius) * (tooth_phase / 0.2)
            elif tooth_phase < 0.4:
                radius = outer_radius
            elif tooth_phase < 0.6:
                radius = outer_radius - (outer_radius - inner_radius) * ((tooth_phase - 0.4) / 0.2)
            else:
                radius = inner_radius
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            # Top face vertex
            vertices.append((x, y, self.thickness / 2))
            # Bottom face vertex
            vertices.append((x, y, -self.thickness / 2))
        
        # Generate faces
        for i in range(total_segments):
            next_i = (i + 1) % total_segments
            
            # Top face triangle
            faces.append((i * 2, next_i * 2, 0))
            
            # Bottom face triangle
            faces.append((1, next_i * 2 + 1, i * 2 + 1))
            
            # Side faces (two triangles per segment)
            faces.append((i * 2, next_i * 2, i * 2 + 1))
            faces.append((next_i * 2, next_i * 2 + 1, i * 2 + 1))
        
        return vertices, faces


class SpringShape(ParametricShape):
    """Generate a parametric spring shape."""
    
    def __init__(self, coils: float, radius: float, wire_radius: float, pitch: float):
        """
        Initialize spring parameters.
        
        Args:
            coils: Number of coils
            radius: Spring radius
            wire_radius: Wire thickness radius
            pitch: Vertical distance between coils
        """
        self.coils = coils
        self.radius = radius
        self.wire_radius = wire_radius
        self.pitch = pitch
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate mesh data for a spring."""
        vertices = []
        faces = []
        
        # Generate spring helix path
        segments_per_coil = 32
        wire_segments = 16
        total_segments = int(self.coils * segments_per_coil)
        
        # Generate vertices along the helix with circular cross-section
        for i in range(total_segments):
            t = (i / segments_per_coil) * 2 * math.pi
            z = (i / segments_per_coil) * self.pitch
            
            # Center point of wire at this position
            cx = self.radius * math.cos(t)
            cy = self.radius * math.sin(t)
            
            # Generate circular cross-section around this point
            for j in range(wire_segments):
                angle = (j / wire_segments) * 2 * math.pi
                
                # Calculate tangent direction for proper orientation
                tx = -math.sin(t)
                ty = math.cos(t)
                
                # Calculate normal in the plane perpendicular to helix
                nx = math.cos(angle) * math.cos(t)
                ny = math.cos(angle) * math.sin(t)
                nz = math.sin(angle)
                
                # Add wire radius offset
                x = cx + self.wire_radius * nx
                y = cy + self.wire_radius * ny
                z_offset = z + self.wire_radius * nz
                
                vertices.append((x, y, z_offset))
        
        # Generate faces
        for i in range(total_segments - 1):
            for j in range(wire_segments):
                next_j = (j + 1) % wire_segments
                
                v1 = i * wire_segments + j
                v2 = i * wire_segments + next_j
                v3 = (i + 1) * wire_segments + j
                v4 = (i + 1) * wire_segments + next_j
                
                # Two triangles per quad
                faces.append((v1, v2, v3))
                faces.append((v2, v4, v3))
        
        return vertices, faces


class ThreadShape(ParametricShape):
    """Generate a parametric thread (screw thread) shape."""
    
    def __init__(self, major_diameter: float, minor_diameter: float, pitch: float, 
                 length: float, thread_angle: float):
        """
        Initialize thread parameters.
        
        Args:
            major_diameter: Outer diameter of thread
            minor_diameter: Inner (root) diameter of thread
            pitch: Distance between threads
            length: Total length of threaded section
            thread_angle: Thread angle in degrees (e.g., 60 for metric)
        """
        self.major_diameter = major_diameter
        self.minor_diameter = minor_diameter
        self.pitch = pitch
        self.length = length
        self.thread_angle = thread_angle
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate mesh data for a thread."""
        vertices = []
        faces = []
        
        major_radius = self.major_diameter / 2
        minor_radius = self.minor_diameter / 2
        
        # Number of turns
        turns = int(self.length / self.pitch)
        segments_per_turn = 32
        total_segments = turns * segments_per_turn
        
        # Generate thread profile vertices
        for i in range(total_segments):
            angle = (i / segments_per_turn) * 2 * math.pi
            z = (i / segments_per_turn) * self.pitch
            
            # Thread profile varies between major and minor radius
            phase = (i % (segments_per_turn // 4)) / (segments_per_turn // 4)
            
            if phase < 0.5:
                # Going from minor to major
                radius = minor_radius + (major_radius - minor_radius) * (phase / 0.5)
            else:
                # Going from major to minor
                radius = major_radius - (major_radius - minor_radius) * ((phase - 0.5) / 0.5)
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            vertices.append((x, y, z))
        
        # Generate faces
        for i in range(total_segments - 1):
            # Create triangular faces between consecutive vertices
            # This is simplified; real thread geometry would be more complex
            faces.append((i, i + 1, 0))
        
        return vertices, faces


class ParametricGenerator:
    """Factory class for creating parametric shapes."""
    
    @staticmethod
    def create_shape(shape_type: str, params: Dict[str, Any]) -> ParametricShape:
        """
        Create a parametric shape based on type and parameters.
        
        Args:
            shape_type: Type of shape ('gear', 'spring', 'thread')
            params: Dictionary of shape-specific parameters
            
        Returns:
            ParametricShape: Instance of the requested shape
            
        Raises:
            ValueError: If shape_type is not supported
        """
        if shape_type == 'gear':
            return GearShape(
                module=params.get('module', 1.0),
                teeth=params.get('teeth', 20),
                pressure_angle=params.get('pressure_angle', 20.0),
                thickness=params.get('thickness', 0.5)
            )
        elif shape_type == 'spring':
            return SpringShape(
                coils=params.get('coils', 5.0),
                radius=params.get('radius', 1.0),
                wire_radius=params.get('wire_radius', 0.1),
                pitch=params.get('pitch', 0.3)
            )
        elif shape_type == 'thread':
            return ThreadShape(
                major_diameter=params.get('major_diameter', 1.0),
                minor_diameter=params.get('minor_diameter', 0.8),
                pitch=params.get('pitch', 0.2),
                length=params.get('length', 2.0),
                thread_angle=params.get('thread_angle', 60.0)
            )
        else:
            raise ValueError(f"Unsupported parametric shape type: {shape_type}")
