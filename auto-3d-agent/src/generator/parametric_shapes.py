"""
Parametric shape generation module for creating specialized 3D shapes
like gears, springs, and threaded components.
"""
import math
import numpy as np
from typing import Dict, Any, Tuple, List


class ParametricShape:
    """Base class for parametric shapes"""
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate vertices and faces for the shape"""
        raise NotImplementedError("Subclasses must implement generate_mesh_data")


class GearShape(ParametricShape):
    """Parametric gear shape generator"""
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate gear mesh with involute tooth profile"""
        module = self.params.get('module', 1.0)
        teeth = self.params.get('teeth', 20)
        pressure_angle = math.radians(self.params.get('pressure_angle', 20.0))
        thickness = self.params.get('thickness', 0.5)
        
        # Calculate gear dimensions
        pitch_diameter = module * teeth
        base_diameter = pitch_diameter * math.cos(pressure_angle)
        outer_diameter = pitch_diameter + 2 * module
        root_diameter = pitch_diameter - 2.5 * module
        
        vertices = []
        faces = []
        
        # Generate gear profile
        tooth_angle = 2 * math.pi / teeth
        resolution = 10  # Points per tooth side
        
        # Front face vertices
        for tooth in range(teeth):
            base_angle = tooth * tooth_angle
            
            # Root circle points
            for i in range(resolution):
                t = i / resolution
                angle = base_angle + t * tooth_angle * 0.4
                r = root_diameter / 2
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                vertices.append((x, y, 0))
            
            # Tooth profile (simplified involute)
            for i in range(resolution):
                t = i / resolution
                angle = base_angle + tooth_angle * 0.4 + t * tooth_angle * 0.2
                r = root_diameter / 2 + (outer_diameter / 2 - root_diameter / 2) * t
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                vertices.append((x, y, 0))
            
            # Top of tooth
            for i in range(resolution):
                t = i / resolution
                angle = base_angle + tooth_angle * 0.6 + t * tooth_angle * 0.2
                r = outer_diameter / 2 - (outer_diameter / 2 - root_diameter / 2) * t
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                vertices.append((x, y, 0))
        
        # Back face vertices (extruded)
        front_count = len(vertices)
        for x, y, z in vertices:
            vertices.append((x, y, thickness))
        
        # Create faces
        points_per_tooth = resolution * 3
        for tooth in range(teeth):
            base_idx = tooth * points_per_tooth
            next_tooth = ((tooth + 1) % teeth) * points_per_tooth
            
            # Front face
            for i in range(points_per_tooth - 1):
                faces.append((base_idx + i, base_idx + i + 1, next_tooth))
            
            # Side faces
            for i in range(points_per_tooth):
                next_i = (i + 1) % points_per_tooth
                v1 = base_idx + i
                v2 = base_idx + next_i
                v3 = v1 + front_count
                v4 = v2 + front_count
                
                faces.append((v1, v2, v3))
                faces.append((v2, v4, v3))
        
        # Back face
        for tooth in range(teeth):
            base_idx = tooth * points_per_tooth + front_count
            next_tooth = ((tooth + 1) % teeth) * points_per_tooth + front_count
            
            for i in range(points_per_tooth - 1):
                faces.append((base_idx + i + 1, base_idx + i, next_tooth))
        
        return vertices, faces


class SpringShape(ParametricShape):
    """Parametric spring shape generator"""
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate helical spring mesh"""
        coils = self.params.get('coils', 5.0)
        radius = self.params.get('radius', 1.0)
        wire_radius = self.params.get('wire_radius', 0.1)
        pitch = self.params.get('pitch', 0.3)
        
        vertices = []
        faces = []
        
        # Generate helix path
        segments_per_coil = 32
        total_segments = int(coils * segments_per_coil)
        cross_section_points = 8  # Circular cross-section
        
        # Generate cross-section circle
        cross_section = []
        for i in range(cross_section_points):
            angle = 2 * math.pi * i / cross_section_points
            cross_section.append((
                wire_radius * math.cos(angle),
                wire_radius * math.sin(angle)
            ))
        
        # Generate vertices along helix
        for seg in range(total_segments + 1):
            t = seg / segments_per_coil
            theta = 2 * math.pi * t
            z = t * pitch
            
            # Center point on helix
            center_x = radius * math.cos(theta)
            center_y = radius * math.sin(theta)
            
            # Tangent direction for proper orientation
            tangent_x = -math.sin(theta)
            tangent_y = math.cos(theta)
            
            # Generate cross-section at this point
            for cx, cy in cross_section:
                # Rotate cross-section to align with helix
                x = center_x + cx * math.cos(theta) - cy * tangent_x
                y = center_y + cx * math.sin(theta) - cy * tangent_y
                z_offset = z + cy * pitch / (2 * math.pi * radius)
                
                vertices.append((x, y, z_offset))
        
        # Generate faces
        for seg in range(total_segments):
            for i in range(cross_section_points):
                next_i = (i + 1) % cross_section_points
                
                v1 = seg * cross_section_points + i
                v2 = seg * cross_section_points + next_i
                v3 = (seg + 1) * cross_section_points + i
                v4 = (seg + 1) * cross_section_points + next_i
                
                faces.append((v1, v2, v4))
                faces.append((v1, v4, v3))
        
        return vertices, faces


class ThreadShape(ParametricShape):
    """Parametric thread shape generator"""
    
    def generate_mesh_data(self) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """Generate threaded cylinder mesh"""
        major_diameter = self.params.get('major_diameter', 1.0)
        minor_diameter = self.params.get('minor_diameter', 0.8)
        pitch = self.params.get('pitch', 0.2)
        length = self.params.get('length', 2.0)
        thread_angle = math.radians(self.params.get('thread_angle', 60.0))
        
        vertices = []
        faces = []
        
        num_threads = int(length / pitch)
        segments_per_thread = 32
        
        # Generate thread profile
        for thread in range(num_threads + 1):
            z_base = thread * pitch
            
            for seg in range(segments_per_thread):
                angle = 2 * math.pi * seg / segments_per_thread
                t = seg / segments_per_thread
                
                # Helical thread profile
                z = z_base + t * pitch
                
                # Thread depth varies sinusoidally
                thread_depth = (major_diameter - minor_diameter) / 2
                r = minor_diameter / 2 + thread_depth * (1 + math.sin(angle * num_threads)) / 2
                
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                
                vertices.append((x, y, z))
        
        # Generate faces
        for thread in range(num_threads):
            for seg in range(segments_per_thread):
                next_seg = (seg + 1) % segments_per_thread
                
                v1 = thread * segments_per_thread + seg
                v2 = thread * segments_per_thread + next_seg
                v3 = (thread + 1) * segments_per_thread + seg
                v4 = (thread + 1) * segments_per_thread + next_seg
                
                faces.append((v1, v2, v4))
                faces.append((v1, v4, v3))
        
        # Add end caps
        center_bottom = len(vertices)
        vertices.append((0, 0, 0))
        center_top = len(vertices)
        vertices.append((0, 0, length))
        
        # Bottom cap
        for seg in range(segments_per_thread):
            next_seg = (seg + 1) % segments_per_thread
            faces.append((center_bottom, next_seg, seg))
        
        # Top cap
        top_ring_start = num_threads * segments_per_thread
        for seg in range(segments_per_thread):
            next_seg = (seg + 1) % segments_per_thread
            faces.append((center_top, top_ring_start + seg, top_ring_start + next_seg))
        
        return vertices, faces


class ParametricGenerator:
    """Factory class for creating parametric shapes"""
    
    @staticmethod
    def create_shape(shape_type: str, params: Dict[str, Any]) -> ParametricShape:
        """Create a parametric shape of the specified type"""
        shape_classes = {
            'gear': GearShape,
            'spring': SpringShape,
            'thread': ThreadShape,
        }
        
        shape_class = shape_classes.get(shape_type.lower())
        if not shape_class:
            raise ValueError(f"Unknown parametric shape type: {shape_type}")
        
        return shape_class(params)
