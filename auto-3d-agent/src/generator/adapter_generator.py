"""
Adapter Generator for 3D Printing
Specializes in creating modification and upgrade parts using Blender.
"""

import bpy
import bmesh
import os
import json
import math
from mathutils import Vector, Matrix
from typing import Dict, List, Tuple, Optional

class AdapterGenerator:
    """Generates 3D printable adapter parts using Blender"""
    
    def __init__(self):
        self.material_properties = {
            'PLA': {'shrinkage': 0.003, 'min_wall': 1.2, 'max_overhang': 45},
            'PETG': {'shrinkage': 0.002, 'min_wall': 1.0, 'max_overhang': 50}, 
            'ABS': {'shrinkage': 0.005, 'min_wall': 1.5, 'max_overhang': 40},
            'TPU': {'shrinkage': 0.002, 'min_wall': 2.0, 'max_overhang': 30}
        }
        
        self.tolerance_classes = {
            'H7/g6': {'shaft': -0.012, 'hole': +0.018},  # Standard fit
            'press-fit': {'shaft': +0.02, 'hole': -0.02},  # Interference
            'sliding-fit': {'shaft': -0.05, 'hole': +0.05}  # Clearance
        }
    
    def clear_scene(self):
        """Clear existing Blender scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    
    def create_cylindrical_adapter(self, geometry: Dict) -> str:
        """Create a cylindrical adapter part"""
        self.clear_scene()
        
        # Extract dimensions
        dims = geometry['dimensions']
        length = dims['length']
        dia_1 = dims['diameter_1'] 
        dia_2 = dims['diameter_2']
        wall_thickness = dims['wall_thickness']
        
        # Create main cylinder body
        bpy.ops.mesh.primitive_cylinder_add(
            radius=max(dia_1, dia_2)/2, 
            depth=length,
            location=(0, 0, 0)
        )
        
        outer_cylinder = bpy.context.active_object
        outer_cylinder.name = "adapter_body"
        
        # Create inner cavities for connections
        self._create_connection_cavity(outer_cylinder, dia_1, length/2, 'end_1')
        self._create_connection_cavity(outer_cylinder, dia_2, length/2, 'end_2')
        
        # Apply modifiers for 3D printing optimization
        self._apply_print_optimizations(outer_cylinder, geometry)
        
        return outer_cylinder.name
    
    def create_bracket_adapter(self, geometry: Dict) -> str:
        """Create a bracket-style adapter"""
        self.clear_scene()
        
        # Create base plate
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=(0, 0, 0)
        )
        
        bracket = bpy.context.active_object
        bracket.name = "bracket_adapter"
        
        # Scale to bracket dimensions
        dims = geometry['dimensions']
        bracket.scale = (dims['width']/2, dims['depth']/2, dims['thickness']/2)
        bpy.ops.object.transform_apply(scale=True)
        
        # Add mounting holes
        self._add_mounting_holes(bracket, geometry.get('mounting_holes', []))
        
        # Add connection features
        self._add_connection_features(bracket, geometry.get('features', []))
        
        return bracket.name
    
    def create_threaded_adapter(self, geometry: Dict) -> str:
        """Create an adapter with threaded connections"""
        self.clear_scene()
        
        # Start with cylindrical base
        adapter_name = self.create_cylindrical_adapter(geometry)
        adapter = bpy.data.objects[adapter_name]
        
        # Add thread geometry
        for feature in geometry.get('features', []):
            if feature['type'] == 'thread':
                self._add_thread_geometry(adapter, feature)
        
        return adapter_name
    
    def _create_connection_cavity(self, obj, diameter: float, depth: float, location: str):
        """Create internal cavity for connection"""
        # Ensure we're in object mode and the target object is active
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')

        # Position cavity based on location
        if location == 'end_1':
            cavity_center = Vector((0, 0, depth/2))
        else:
            cavity_center = Vector((0, 0, -depth/2))
        
        # Create cylinder for boolean subtraction
        bpy.ops.mesh.primitive_cylinder_add(
            radius=diameter/2,
            depth=depth,
            location=cavity_center
        )
        
        cavity = bpy.context.active_object
        cavity.name = f"cavity_{location}"
        
        # Apply boolean modifier
        modifier = obj.modifiers.new(name=f"Boolean_{location}", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = cavity
        
        # Hide the cavity object
        cavity.hide_set(True)
    
    def _add_mounting_holes(self, obj, holes: List[Dict]):
        """Add mounting holes to bracket"""
        for i, hole in enumerate(holes):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=hole['diameter']/2,
                depth=hole['depth'],
                location=hole['position']
            )
            
            hole_obj = bpy.context.active_object
            hole_obj.name = f"mounting_hole_{i}"
            
            # Boolean subtract from main object
            modifier = obj.modifiers.new(name=f"Hole_{i}", type='BOOLEAN')
            modifier.operation = 'DIFFERENCE'
            modifier.object = hole_obj
            
            hole_obj.hide_set(True)
    
    def _add_connection_features(self, obj, features: List[Dict]):
        """Add connection features like bosses, tabs, etc."""
        for i, feature in enumerate(features):
            if feature['type'] == 'boss':
                self._create_boss(obj, feature, i)
            elif feature['type'] == 'tab':
                self._create_tab(obj, feature, i)
            elif feature['type'] == 'slot':
                self._create_slot(obj, feature, i)
    
    def _create_boss(self, obj, feature: Dict, index: int):
        """Create a cylindrical boss"""
        bpy.ops.mesh.primitive_cylinder_add(
            radius=feature['diameter']/2,
            depth=feature['height'],
            location=feature['position']
        )
        
        boss = bpy.context.active_object
        boss.name = f"boss_{index}"
        
        # Boolean union with main object
        modifier = obj.modifiers.new(name=f"Boss_{index}", type='BOOLEAN')
        modifier.operation = 'UNION'
        modifier.object = boss
        
        boss.hide_set(True)
    
    def _create_tab(self, obj, feature: Dict, index: int):
        """Create a rectangular tab"""
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=feature['position']
        )
        
        tab = bpy.context.active_object
        tab.name = f"tab_{index}"
        
        # Scale to tab dimensions
        dims = feature['dimensions']
        tab.scale = (dims['width']/2, dims['length']/2, dims['thickness']/2)
        bpy.ops.object.transform_apply(scale=True)
        
        # Boolean union
        modifier = obj.modifiers.new(name=f"Tab_{index}", type='BOOLEAN')
        modifier.operation = 'UNION'
        modifier.object = tab
        
        tab.hide_set(True)
    
    def _create_slot(self, obj, feature: Dict, index: int):
        """Create a slot for tab insertion"""
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=feature['position']
        )
        
        slot = bpy.context.active_object
        slot.name = f"slot_{index}"
        
        # Scale slot with tolerance
        dims = feature['dimensions']
        tolerance = 0.2  # 0.2mm clearance
        slot.scale = (
            (dims['width'] + tolerance)/2, 
            (dims['length'] + tolerance)/2, 
            (dims['depth'] + tolerance)/2
        )
        bpy.ops.object.transform_apply(scale=True)
        
        # Boolean subtract
        modifier = obj.modifiers.new(name=f"Slot_{index}", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = slot
        
        slot.hide_set(True)
    
    def _add_thread_geometry(self, obj, thread_spec: Dict):
        """Add simplified thread geometry"""
        # For 3D printing, we often use simplified threads
        # Real threads would require post-processing (tapping/threading)
        
        pitch = thread_spec.get('pitch', 1.25)
        location = thread_spec.get('location', 'end_1')
        
        # Create thread relief grooves for better printing
        # This is a simplified approach - real threads need more complex geometry
        pass
    
    def _apply_print_optimizations(self, obj, geometry: Dict):
        """Apply optimizations for 3D printing"""
        print_features = geometry.get('print_features', {})
        
        # Add chamfers to reduce sharp edges
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Add bevel modifier for chamfers
        bpy.ops.object.mode_set(mode='OBJECT')
        bevel_modifier = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel_modifier.width = 0.5  # 0.5mm chamfer
        bevel_modifier.segments = 2
        
        # Add subdivision for smoother surfaces if needed
        if print_features.get('smooth_surfaces', False):
            subdiv_modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subdiv_modifier.levels = 1
    
    def optimize_for_print_orientation(self, obj_name: str, orientation: str) -> Dict:
        """Optimize geometry for specific print orientation"""
        obj = bpy.data.objects[obj_name]
        
        orientations = {
            'xy': (0, 0, 0),      # Flat on bed
            'xz': (90, 0, 0),     # Standing on edge
            'yz': (0, 90, 0),     # Side orientation
            'vertical': (0, 0, 0) # Custom vertical
        }
        
        if orientation in orientations:
            rotation = orientations[orientation]
            obj.rotation_euler = [math.radians(r) for r in rotation]
        
        # Analyze for supports needed
        support_analysis = self._analyze_support_requirements(obj)
        
        return {
            'orientation': orientation,
            'supports_needed': support_analysis['supports_needed'],
            'overhang_areas': support_analysis['overhang_areas'],
            'print_time_estimate': support_analysis['print_time_estimate']
        }
    
    def _analyze_support_requirements(self, obj) -> Dict:
        """Analyze if supports are needed for printing"""
        # This would analyze overhangs and unsupported geometry
        # For now, returning mock analysis
        
        return {
            'supports_needed': False,
            'overhang_areas': [],
            'print_time_estimate': "2h 15m"
        }
    
    def generate_adapter(self, geometry: Dict, output_path: str) -> Dict:
        """Main function to generate adapter geometry"""
        
        # Determine adapter type and create geometry
        adapter_type = geometry.get('type', 'cylindrical_adapter')
        
        if adapter_type == 'cylindrical_adapter':
            adapter_name = self.create_cylindrical_adapter(geometry)
        elif adapter_type == 'bracket_adapter':
            adapter_name = self.create_bracket_adapter(geometry)
        elif adapter_type == 'threaded_adapter':
            adapter_name = self.create_threaded_adapter(geometry)
        else:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
        
        # Optimize for print orientation
        print_orientation = geometry.get('print_orientation', 'auto')
        if print_orientation == 'auto':
            print_orientation = self._determine_optimal_orientation(geometry)
        
        orientation_result = self.optimize_for_print_orientation(adapter_name, print_orientation)
        
        # Apply final modifiers
        self._apply_final_modifiers(adapter_name)
        
        # Export the model
        export_result = self._export_model(adapter_name, output_path)
        
        return {
            'success': True,
            'adapter_name': adapter_name,
            'geometry_type': adapter_type,
            'print_optimization': orientation_result,
            'export_files': export_result,
            'recommendations': [
                f"Print with 0.2mm layer height",
                f"Use 100% infill for mechanical strength",
                f"Orient part as: {print_orientation}",
                "Consider post-processing for threaded features"
            ]
        }
    
    def _determine_optimal_orientation(self, geometry: Dict) -> str:
        """Determine optimal print orientation automatically"""
        # Analyze geometry to suggest best orientation
        adapter_type = geometry.get('type', 'cylindrical_adapter')
        
        if adapter_type == 'cylindrical_adapter':
            return 'vertical'  # Usually best for cylindrical parts
        elif adapter_type == 'bracket_adapter':
            return 'xy'  # Flat on bed for brackets
        else:
            return 'xy'  # Default to flat
    
    def _apply_final_modifiers(self, obj_name: str):
        """Apply final modifiers before export"""
        obj = bpy.data.objects[obj_name]
        
        # Apply all modifiers
        bpy.context.view_layer.objects.active = obj
        for modifier in obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    
    def _export_model(self, obj_name: str, output_path: str) -> Dict:
        """Export the model in multiple formats"""
        obj = bpy.data.objects[obj_name]
        
        # Select only the adapter object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        export_files = {}
        
        # Export STL (primary for 3D printing)
        stl_path = os.path.join(output_path, f"{obj_name}.stl")
        bpy.ops.export_mesh.stl(filepath=stl_path, use_selection=True)
        export_files['stl'] = stl_path
        
        # Export OBJ (for visualization)
        obj_path = os.path.join(output_path, f"{obj_name}.obj")
        bpy.ops.export_scene.obj(filepath=obj_path, use_selection=True)
        export_files['obj'] = obj_path
        
        # Export 3MF (modern 3D printing format) if available
        try:
            if hasattr(bpy.ops.export_mesh, 'threemf'):
                threemf_path = os.path.join(output_path, f"{obj_name}.3mf")
                bpy.ops.export_mesh.threemf(filepath=threemf_path, use_selection=True)
                export_files['3mf'] = threemf_path
        except Exception as e:
            print(f"3MF export skipped: {e}")
        
        return export_files

if __name__ == "__main__":
    # Example usage (would be called from main pipeline)
    generator = AdapterGenerator()
    
    # Mock geometry for testing
    test_geometry = {
        'type': 'cylindrical_adapter',
        'dimensions': {
            'length': 25,
            'diameter_1': 10.2,
            'diameter_2': 8.2, 
            'wall_thickness': 2
        },
        'print_orientation': 'vertical',
        'print_features': {
            'layer_height': 0.2,
            'infill_percentage': 100
        }
    }
    
    print("Adapter Generator initialized and ready for 3D printing adapter creation")
