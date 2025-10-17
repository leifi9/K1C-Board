"""
STL Exporter optimized for 3D Printing
Handles export with print-specific optimizations and validation.
"""

import os
import struct
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

class STLExporter:
    """Exports 3D models to STL format with 3D printing optimizations"""
    
    def __init__(self):
        self.export_settings = {
            'units': 'mm',  # Always millimeters for 3D printing
            'precision': 6,  # Decimal precision
            'merge_vertices': True,  # Merge duplicate vertices
            'fix_normals': True,  # Ensure correct normal directions
            'manifold_check': True,  # Validate manifold geometry
            'minimum_feature_size': 0.4  # Minimum printable feature size in mm
        }
    
    def export_ascii_stl(self, vertices: np.ndarray, faces: np.ndarray, 
                        output_path: str, part_name: str = "adapter") -> Dict:
        """Export ASCII STL format"""
        
        # Validate input geometry
        validation_result = self._validate_geometry(vertices, faces)
        if not validation_result['is_valid']:
            return {
                'success': False,
                'error': validation_result['errors'],
                'file_path': None
            }
        
        # Calculate face normals
        normals = self._calculate_face_normals(vertices, faces)
        
        try:
            with open(output_path, 'w') as f:
                # Write STL header
                f.write(f"solid {part_name}\n")
                
                # Write triangles
                for i, face in enumerate(faces):
                    normal = normals[i]
                    
                    # Write facet normal
                    f.write(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
                    f.write(f"    outer loop\n")
                    
                    # Write vertices
                    for vertex_idx in face:
                        vertex = vertices[vertex_idx]
                        f.write(f"      vertex {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
                    
                    f.write(f"    endloop\n")
                    f.write(f"  endfacet\n")
                
                # Write STL footer
                f.write(f"endsolid {part_name}\n")
            
            # Get file info
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'format': 'ASCII STL',
                'file_size_kb': file_size / 1024,
                'triangle_count': len(faces),
                'validation': validation_result,
                'print_recommendations': self._generate_print_recommendations(vertices, faces)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to write STL file: {str(e)}",
                'file_path': None
            }
    
    def export_binary_stl(self, vertices: np.ndarray, faces: np.ndarray, 
                         output_path: str, part_name: str = "adapter") -> Dict:
        """Export binary STL format (more compact)"""
        
        # Validate input geometry
        validation_result = self._validate_geometry(vertices, faces)
        if not validation_result['is_valid']:
            return {
                'success': False,
                'error': validation_result['errors'],
                'file_path': None
            }
        
        # Calculate face normals
        normals = self._calculate_face_normals(vertices, faces)
        
        try:
            with open(output_path, 'wb') as f:
                # Write 80-byte header
                header = part_name.encode('utf-8')[:80].ljust(80, b'\0')
                f.write(header)
                
                # Write triangle count
                triangle_count = len(faces)
                f.write(struct.pack('<I', triangle_count))
                
                # Write triangles
                for i, face in enumerate(faces):
                    normal = normals[i]
                    
                    # Pack normal (3 floats)
                    f.write(struct.pack('<fff', normal[0], normal[1], normal[2]))
                    
                    # Pack vertices (9 floats)
                    for vertex_idx in face:
                        vertex = vertices[vertex_idx]
                        f.write(struct.pack('<fff', vertex[0], vertex[1], vertex[2]))
                    
                    # Write attribute byte count (usually 0)
                    f.write(struct.pack('<H', 0))
            
            # Get file info
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'file_path': output_path,
                'format': 'Binary STL',
                'file_size_kb': file_size / 1024,
                'triangle_count': len(faces),
                'validation': validation_result,
                'print_recommendations': self._generate_print_recommendations(vertices, faces)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to write binary STL file: {str(e)}",
                'file_path': None
            }
    
    def _validate_geometry(self, vertices: np.ndarray, faces: np.ndarray) -> Dict:
        """Validate geometry for 3D printing"""
        errors = []
        warnings = []
        
        # Check for minimum vertices
        if len(vertices) < 3:
            errors.append("Insufficient vertices (minimum 3 required)")
        
        # Check for minimum faces
        if len(faces) < 1:
            errors.append("No faces found")
        
        # Check face indices
        max_vertex_idx = len(vertices) - 1
        for i, face in enumerate(faces):
            for vertex_idx in face:
                if vertex_idx > max_vertex_idx:
                    errors.append(f"Face {i} references non-existent vertex {vertex_idx}")
        
        # Check for degenerate triangles
        degenerate_count = 0
        for i, face in enumerate(faces):
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            
            # Calculate triangle area
            edge1 = v2 - v1
            edge2 = v3 - v1
            cross = np.cross(edge1, edge2)
            area = np.linalg.norm(cross) / 2.0
            
            if area < 1e-10:  # Very small area
                degenerate_count += 1
        
        if degenerate_count > 0:
            warnings.append(f"Found {degenerate_count} degenerate triangles")
        
        # Check bounding box size
        if len(vertices) > 0:
            bbox_min = np.min(vertices, axis=0)
            bbox_max = np.max(vertices, axis=0)
            dimensions = bbox_max - bbox_min
            
            # Check for very small parts
            min_dimension = np.min(dimensions)
            if min_dimension < self.export_settings['minimum_feature_size']:
                warnings.append(f"Part has features smaller than {self.export_settings['minimum_feature_size']}mm")
            
            # Check for very large parts
            max_dimension = np.max(dimensions)
            if max_dimension > 300:  # Larger than typical print bed
                warnings.append(f"Part dimension ({max_dimension:.1f}mm) exceeds typical printer build volume")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'degenerate_triangles': degenerate_count if len(faces) > 0 else 0,
            'manifold_edges': self._check_manifold(vertices, faces) if len(faces) > 0 else True
        }
    
    def _calculate_face_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Calculate face normals for triangles"""
        normals = np.zeros((len(faces), 3))
        
        for i, face in enumerate(faces):
            v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
            
            # Calculate normal using cross product
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = np.cross(edge1, edge2)
            
            # Normalize
            norm = np.linalg.norm(normal)
            if norm > 1e-10:
                normal = normal / norm
            
            normals[i] = normal
        
        return normals
    
    def _check_manifold(self, vertices: np.ndarray, faces: np.ndarray) -> bool:
        """Check if mesh is manifold (each edge shared by exactly 2 faces)"""
        edge_count = {}
        
        for face in faces:
            # Check all 3 edges of the triangle
            edges = [
                tuple(sorted([face[0], face[1]])),
                tuple(sorted([face[1], face[2]])),
                tuple(sorted([face[2], face[0]]))
            ]
            
            for edge in edges:
                edge_count[edge] = edge_count.get(edge, 0) + 1
        
        # Manifold mesh: each edge should appear exactly 2 times
        for edge, count in edge_count.items():
            if count != 2:
                return False
        
        return True
    
    def _generate_print_recommendations(self, vertices: np.ndarray, faces: np.ndarray) -> List[str]:
        """Generate 3D printing recommendations based on geometry"""
        recommendations = []
        
        if len(vertices) == 0:
            return recommendations
        
        # Analyze bounding box
        bbox_min = np.min(vertices, axis=0)
        bbox_max = np.max(vertices, axis=0)
        dimensions = bbox_max - bbox_min
        
        # Layer height recommendation
        min_feature = np.min(dimensions)
        if min_feature < 2.0:
            recommendations.append("Use 0.1mm layer height for fine details")
        elif min_feature < 10.0:
            recommendations.append("Use 0.15-0.2mm layer height")
        else:
            recommendations.append("Use 0.2-0.3mm layer height for faster printing")
        
        # Infill recommendation
        max_dimension = np.max(dimensions)
        if max_dimension > 50:
            recommendations.append("Consider using 20-40% infill to save material")
        else:
            recommendations.append("Use 100% infill for mechanical parts")
        
        # Support analysis
        z_range = bbox_max[2] - bbox_min[2]
        if z_range > dimensions[0] and z_range > dimensions[1]:
            recommendations.append("Tall part - consider printing supports")
        
        # Wall thickness
        if min_feature < 1.0:
            recommendations.append("Warning: Features thinner than 1mm may not print reliably")
        
        return recommendations
    
    def export_with_metadata(self, vertices: np.ndarray, faces: np.ndarray, 
                           output_path: str, metadata: Dict) -> Dict:
        """Export STL with accompanying metadata file"""
        
        # Export the STL file (binary for efficiency)
        stl_result = self.export_binary_stl(vertices, faces, output_path, 
                                          metadata.get('part_name', 'adapter'))
        
        if stl_result['success']:
            # Create metadata file
            metadata_path = output_path.replace('.stl', '_metadata.json')
            
            full_metadata = {
                'part_info': metadata,
                'export_info': {
                    'format': stl_result['format'],
                    'triangle_count': stl_result['triangle_count'],
                    'file_size_kb': stl_result['file_size_kb']
                },
                'print_recommendations': stl_result['print_recommendations'],
                'validation_results': stl_result['validation'],
                'export_settings': self.export_settings
            }
            
            try:
                with open(metadata_path, 'w') as f:
                    json.dump(full_metadata, f, indent=2)
                
                stl_result['metadata_file'] = metadata_path
                
            except Exception as e:
                stl_result['metadata_warning'] = f"Could not write metadata: {str(e)}"
        
        return stl_result

if __name__ == "__main__":
    # Example usage
    exporter = STLExporter()
    
    # Create simple test cube
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom face
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Top face
    ], dtype=np.float32)
    
    faces = np.array([
        [0, 1, 2], [0, 2, 3],  # Bottom
        [4, 6, 5], [4, 7, 6],  # Top  
        [0, 4, 5], [0, 5, 1],  # Front
        [2, 6, 7], [2, 7, 3],  # Back
        [0, 3, 7], [0, 7, 4],  # Left
        [1, 5, 6], [1, 6, 2]   # Right
    ], dtype=np.uint32)
    
    print("STL Exporter initialized and ready for 3D printing export")
