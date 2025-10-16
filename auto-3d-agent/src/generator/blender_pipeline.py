import bpy
import math
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from .model_interface import ModelInterface

class BlenderPipeline(ModelInterface):
    def __init__(self):
        self.clear_scene()
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    def export_to_cad(self, model_path: str, format: str = 'STEP') -> str:
        """
        Export a generated model to CAD format with topology optimization
        """
        try:
            import FreeCAD as App
            import Part
            import Mesh
            from pathlib import Path

            # Load the mesh
            mesh = Mesh.Mesh(model_path)

            # Create a new document
            doc = App.newDocument("Conversion")

            # Convert mesh to shape with topology optimization
            shape = self._optimize_mesh_topology(mesh)

            # Create a new part
            part = doc.addObject("Part::Feature", "OptimizedPart")
            part.Shape = shape

            # Export path
            output_path = Path(model_path)
            if format.upper() == 'STEP':
                output_path = output_path.with_suffix('.step')
                Part.export([part], str(output_path))
            elif format.upper() == 'IGES':
                output_path = output_path.with_suffix('.iges')
                Part.export([part], str(output_path))
            else:
                raise ValueError(f"Unsupported format: {format}")

            return str(output_path)
        except ImportError:
            # Fallback: just copy the file with new extension
            from pathlib import Path
            output_path = Path(model_path)
            if format.upper() == 'STEP':
                output_path = output_path.with_suffix('.step')
            elif format.upper() == 'IGES':
                output_path = output_path.with_suffix('.iges')
            else:
                output_path = output_path.with_suffix('.cad')
            import shutil
            shutil.copy(model_path, output_path)
            return str(output_path)

    def _optimize_mesh_topology(self, mesh: 'Mesh.Mesh') -> 'Part.Shape':
        """
        Optimize mesh topology for better CAD conversion
        """
        # Convert mesh to shape
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh.Topology, 0.1)
        
        # Attempt to recognize basic shapes
        recognized_shapes = []
        
        # Try to fit planes
        planes = self._fit_planes(shape)
        recognized_shapes.extend(planes)
        
        # Try to fit cylinders
        cylinders = self._fit_cylinders(shape)
        recognized_shapes.extend(cylinders)
        
        # If we found any recognized shapes, use them
        if recognized_shapes:
            # Create a compound shape
            compound = Part.makeCompound(recognized_shapes)
            
            # Try to heal the shape
            healed_shape = self._heal_shape(compound)
            return healed_shape
            
        # Fallback: optimize the original shape
        return self._heal_shape(shape)
        
    def _fit_planes(self, shape: 'Part.Shape') -> List['Part.Face']:
        """Attempt to recognize and fit planar surfaces"""
        planes = []
        tol = 0.1  # Tolerance for planarity
        
        # Analyze faces
        for face in shape.Faces:
            if face.Surface.isPlanar():
                # Get the face bounds
                bounds = face.BoundBox
                
                # Create a new planar face
                plane = Part.makePlane(
                    bounds.XLength,
                    bounds.YLength,
                    App.Vector(bounds.XMin, bounds.YMin, bounds.ZMin)
                )
                
                planes.append(plane)
                
        return planes
        
    def _fit_cylinders(self, shape: 'Part.Shape') -> List['Part.Face']:
        """Attempt to recognize and fit cylindrical surfaces"""
        cylinders = []
        tol = 0.1  # Tolerance for cylindrical fit
        
        # Analyze faces
        for face in shape.Faces:
            if hasattr(face.Surface, 'Radius'):  # Cylindrical surface
                # Get cylinder parameters
                radius = face.Surface.Radius
                axis = face.Surface.Axis
                location = face.Surface.Location
                
                # Create a new cylindrical face
                height = face.BoundBox.ZLength
                cylinder = Part.makeCylinder(radius, height, location, axis)
                
                cylinders.append(cylinder)
                
        return cylinders
        
    def _heal_shape(self, shape: 'Part.Shape') -> 'Part.Shape':
        """Heal shape topology"""
        # Fix self-intersections
        fixed_shape = shape.removeSplitter()
        
        # Fix small edges
        fixed_shape = self._remove_small_edges(fixed_shape)
        
        # Fix small faces
        fixed_shape = self._remove_small_faces(fixed_shape)
        
        # Sew faces
        fixed_shape = self._sew_faces(fixed_shape)
        
        return fixed_shape
        
    def _remove_small_edges(self, shape: 'Part.Shape', 
                          min_length: float = 0.1) -> 'Part.Shape':
        """Remove edges smaller than min_length"""
        edges_to_remove = []
        for edge in shape.Edges:
            if edge.Length < min_length:
                edges_to_remove.append(edge)
                
        if edges_to_remove:
            shape = shape.removeShape(edges_to_remove)
            
        return shape
        
    def _remove_small_faces(self, shape: 'Part.Shape',
                           min_area: float = 0.01) -> 'Part.Shape':
        """Remove faces smaller than min_area"""
        faces_to_remove = []
        for face in shape.Faces:
            if face.Area < min_area:
                faces_to_remove.append(face)
                
        if faces_to_remove:
            shape = shape.removeShape(faces_to_remove)
            
        return shape
        
    def _sew_faces(self, shape: 'Part.Shape',
                   tolerance: float = 0.1) -> 'Part.Shape':
        """Sew faces together"""
        # Create a shell
        shell = Part.Shell(shape.Faces)
        
        # Try to make solid
        try:
            solid = Part.Solid(shell)
            return solid
        except:
            # If we can't make a solid, return the shell
            return shell

    def clear_scene(self):
        """Clear the current Blender scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

    def process_input_images(self, images: List[str]) -> Dict[str, Any]:
        """Process input images for reference"""
        if not images:
            return {}
        
        from ..ingestion.image_processor import ImageProcessor
        
        image_processor = ImageProcessor()
        processed_images = []
        
        for image_path in images:
            result = image_processor.process_image(image_path)
            processed_images.append(result)
        
        # Aggregate features
        all_shapes = []
        all_colors = []
        total_features = 0
        
        for img_data in processed_images:
            if 'shapes' in img_data:
                all_shapes.extend(img_data['shapes'])
            if 'colors' in img_data:
                all_colors.extend(img_data['colors'])
            if 'features' in img_data:
                total_features += len(img_data['features'])
        
        return {
            'image_count': len(images),
            'processed': processed_images,
            'shapes_detected': all_shapes,
            'dominant_colors': all_colors[:3] if all_colors else [],
            'total_features': total_features
        }
    
    def process_input_videos(self, videos: List[str]) -> Dict[str, Any]:
        """Process input videos for reference"""
        if not videos:
            return {}
        
        from ..ingestion.video_processor import VideoProcessor
        
        video_processor = VideoProcessor()
        processed_videos = []
        total_frames = 0
        
        for video_path in videos:
            result = video_processor.process_video(video_path)
            processed_videos.append(result)
            total_frames += len(result)
        
        return {
            'video_count': len(videos),
            'processed': processed_videos,
            'total_frames_analyzed': total_frames
        }
    
    def process_input_links(self, links: List[str]) -> Dict[str, Any]:
        """Process input web links for reference"""
        if not links:
            return {}
        
        from ..retriever.web_search import WebSearch
        
        web_search = WebSearch()
        processed_links = []
        
        for link in links:
            # Treat each link as a search result
            result = web_search.fetch_results([{'url': link, 'title': '', 'snippet': ''}])
            if result:
                processed_links.extend(result)
        
        return {
            'link_count': len(links),
            'processed': processed_links,
            'content_fetched': len(processed_links)
        }

    def generate_model(self, description: str, 
                      images: Optional[List[str]] = None,
                      videos: Optional[List[str]] = None,
                      links: Optional[List[str]] = None) -> str:
        """
        Generate a 3D model based on the provided inputs
        Returns: Path to the generated model file
        """
        # Process all inputs
        image_features = self.process_input_images(images or [])
        video_features = self.process_input_videos(videos or [])
        link_features = self.process_input_links(links or [])
        
        # Extract parameters from description and features
        params = self._extract_params_from_description(description)
        
        # Update parameters based on image analysis
        if image_features:
            self._update_params_from_features(params, image_features)
            
        # Check for parametric shape requirements
        if self._is_parametric_shape(description, params):
            obj_name = self._create_parametric_shape(params)
        else:
            # Create standard mesh
            obj_name = self._create_base_mesh(params)
            
        # Apply modifiers based on parameters
        self._apply_modifiers(obj_name, params)
        
        # Export to temporary file
        temp_file = self.temp_dir / "temp_model.stl"
        self._export_mesh(temp_file)
        
        return str(temp_file)
        
    def _is_parametric_shape(self, description: str, params: Dict[str, Any]) -> bool:
        """Determine if we should use parametric generation"""
        desc_lower = description.lower()
        
        # Check for specific parametric shape keywords
        parametric_indicators = {
            'gear': ['gear', 'zahnrad', 'getriebe'],
            'spring': ['spring', 'feder', 'sprungfeder'],
            'thread': ['thread', 'gewinde', 'schraube']
        }
        
        for shape_type, keywords in parametric_indicators.items():
            if any(keyword in desc_lower for keyword in keywords):
                params['parametric_type'] = shape_type
                return True
                
        return False
        
    def _create_parametric_shape(self, params: Dict[str, Any]) -> str:
        """Create a mesh from parametric shape"""
        from .parametric_shapes import ParametricGenerator
        
        # Get shape type and specific parameters
        shape_type = params['parametric_type']
        shape_params = self._extract_shape_params(shape_type, params)
        
        # Generate shape
        shape = ParametricGenerator.create_shape(shape_type, shape_params)
        vertices, faces = shape.generate_mesh_data()
        
        # Create mesh in Blender
        mesh = bpy.data.meshes.new(name=f"Parametric_{shape_type}")
        obj = bpy.data.objects.new(mesh.name, mesh)
        
        # Create the mesh from vertices and faces
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        
        # Link object to scene
        bpy.context.scene.collection.objects.link(obj)
        
        return obj.name
        
    def _extract_shape_params(self, shape_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific parameters for different shape types"""
        if shape_type == 'gear':
            return {
                'module': params.get('gear_module', 1.0),
                'teeth': params.get('gear_teeth', 20),
                'pressure_angle': params.get('pressure_angle', 20.0),
                'thickness': params.get('thickness', 0.5)
            }
        elif shape_type == 'spring':
            return {
                'coils': params.get('spring_coils', 5.0),
                'radius': params.get('spring_radius', 1.0),
                'wire_radius': params.get('wire_radius', 0.1),
                'pitch': params.get('spring_pitch', 0.3)
            }
        elif shape_type == 'thread':
            return {
                'major_diameter': params.get('thread_diameter', 1.0),
                'minor_diameter': params.get('thread_diameter', 1.0) * 0.8,
                'pitch': params.get('thread_pitch', 0.2),
                'length': params.get('thread_length', 2.0),
                'thread_angle': params.get('thread_angle', 60.0)
            }
        return {}
    
    def _update_params_from_features(self, params: Dict[str, Any], features: Dict[str, Any]):
        """Update parameters based on image/video features"""
        if not features:
            return
        
        # Extract shape information from detected shapes
        if 'shapes_detected' in features:
            shapes = features['shapes_detected']
            if shapes:
                # Get most common shape type
                shape_counts = {}
                for shape in shapes:
                    shape_type = shape.get('type', 'unknown')
                    shape_counts[shape_type] = shape_counts.get(shape_type, 0) + 1
                
                if shape_counts:
                    dominant_shape = max(shape_counts, key=shape_counts.get)
                    if dominant_shape in ['circle', 'sphere']:
                        params['type'] = 'sphere'
                    elif dominant_shape in ['rectangle', 'square']:
                        params['type'] = 'cube'
        
        # Update size based on feature count
        if 'total_features' in features:
            feature_count = features['total_features']
            if feature_count > 50:
                params['modifiers']['subdivision'] = {'levels': 2}
    
    def _extract_params_from_description(self, description: str) -> Dict[str, Any]:
        """Extract parameters from text description"""
        params = {
            'type': 'cube',
            'size': 1.0,
            'modifiers': {}
        }
        
        # Basic keyword detection (will be enhanced with NLP)
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['sphere', 'ball', 'round']):
            params['type'] = 'sphere'
        elif any(word in desc_lower for word in ['cylinder', 'tube', 'pipe']):
            params['type'] = 'cylinder'
        
        # Extract size information
        if 'small' in desc_lower:
            params['size'] = 0.5
        elif 'large' in desc_lower:
            params['size'] = 2.0
            
        # Extract modifier information
        if 'smooth' in desc_lower:
            params['modifiers']['subdivision'] = {'levels': 2}
        if 'rounded' in desc_lower:
            params['modifiers']['bevel'] = {'width': 0.05}
            
        return params
    
    def _create_base_mesh(self, params: Dict[str, Any]) -> str:
        """Create the base mesh with advanced geometry operations"""
        mesh_type = params.get('type', 'cube')
        dimensions = params.get('dimensions', {'width': 1.0, 'height': 1.0, 'depth': 1.0})
        
        # Create base object
        obj_name = self._create_primitive(mesh_type, dimensions)
        
        # Apply modifiers based on parameters
        if params.get('generation_hints', {}).get('use_symmetry', False):
            self._apply_symmetry(obj_name)
            
        if params.get('boolean_operations'):
            self._apply_boolean_operations(obj_name, params['boolean_operations'])
            
        if params.get('deformations'):
            self._apply_deformations(obj_name, params['deformations'])
            
        return obj_name
        
    def _create_primitive(self, mesh_type: str, dimensions: Dict[str, float]) -> str:
        """Create a primitive mesh with given dimensions"""
        width = dimensions.get('width', 1.0)
        height = dimensions.get('height', 1.0)
        depth = dimensions.get('depth', 1.0)
        
        if mesh_type == 'cube':
            bpy.ops.mesh.primitive_cube_add()
            obj = bpy.context.active_object
            obj.scale = (width, depth, height)
            
        elif mesh_type == 'sphere':
            segments = 32  # Higher for smoother sphere
            bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=segments//2)
            obj = bpy.context.active_object
            obj.scale = (width, depth, height)
            
        elif mesh_type == 'cylinder':
            vertices = 32  # Higher for smoother cylinder
            bpy.ops.mesh.primitive_cylinder_add(vertices=vertices)
            obj = bpy.context.active_object
            obj.scale = (width, depth, height)
            
        elif mesh_type == 'cone':
            vertices = 32
            bpy.ops.mesh.primitive_cone_add(vertices=vertices)
            obj = bpy.context.active_object
            obj.scale = (width, depth, height)
            
        elif mesh_type == 'torus':
            major_radius = max(width, depth) / 2
            minor_radius = min(width, depth) / 4
            bpy.ops.mesh.primitive_torus_add(
                major_segments=48,
                minor_segments=24,
                major_radius=major_radius,
                minor_radius=minor_radius
            )
            obj = bpy.context.active_object
            obj.scale = (1.0, 1.0, height)
            
        else:
            raise ValueError(f"Unsupported mesh type: {mesh_type}")
            
        return obj.name
        
    def _apply_symmetry(self, obj_name: str):
        """Apply mirror modifier for symmetry"""
        obj = bpy.data.objects[obj_name]
        mirror = obj.modifiers.new(name="Mirror", type='MIRROR')
        mirror.use_axis[0] = True  # X-axis
        mirror.use_clip = True
        
    def _apply_boolean_operations(self, obj_name: str, operations: List[Dict[str, Any]]):
        """Apply boolean operations with other meshes"""
        main_obj = bpy.data.objects[obj_name]
        
        for op in operations:
            # Create the boolean object
            bool_obj_name = self._create_primitive(
                op.get('type', 'cube'),
                op.get('dimensions', {'width': 0.5, 'height': 0.5, 'depth': 0.5})
            )
            bool_obj = bpy.data.objects[bool_obj_name]
            
            # Position the boolean object
            bool_obj.location = op.get('position', (0, 0, 0))
            bool_obj.rotation_euler = op.get('rotation', (0, 0, 0))
            
            # Create boolean modifier
            boolean = main_obj.modifiers.new(name="Boolean", type='BOOLEAN')
            boolean.object = bool_obj
            boolean.operation = op.get('operation', 'DIFFERENCE').upper()
            
    def _apply_deformations(self, obj_name: str, deformations: List[Dict[str, Any]]):
        """Apply various deformation modifiers"""
        obj = bpy.data.objects[obj_name]
        
        for deform in deformations:
            deform_type = deform.get('type', '').upper()
            
            if deform_type == 'BEND':
                mod = obj.modifiers.new(name="Bend", type='SIMPLE_DEFORM')
                mod.deform_method = 'BEND'
                mod.angle = deform.get('angle', 1.5708)  # 90 degrees
                mod.deform_axis = deform.get('axis', 'X').upper()
                
            elif deform_type == 'TWIST':
                mod = obj.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
                mod.deform_method = 'TWIST'
                mod.angle = deform.get('angle', 1.5708)
                mod.deform_axis = deform.get('axis', 'Z').upper()
                
            elif deform_type == 'TAPER':
                mod = obj.modifiers.new(name="Taper", type='SIMPLE_DEFORM')
                mod.deform_method = 'TAPER'
                mod.factor = deform.get('factor', 1.0)
                mod.deform_axis = deform.get('axis', 'Z').upper()
                
            elif deform_type == 'LATTICE':
                # Create lattice object
                bpy.ops.object.add(type='LATTICE', enter_editmode=False)
                lattice = bpy.context.active_object
                lattice.scale = deform.get('scale', (2.0, 2.0, 2.0))
                
                # Setup lattice modifier
                mod = obj.modifiers.new(name="Lattice", type='LATTICE')
                mod.object = lattice
                
                # Configure lattice resolution
                lattice.data.points_u = deform.get('resolution_u', 2)
                lattice.data.points_v = deform.get('resolution_v', 2)
                lattice.data.points_w = deform.get('resolution_w', 2)
                
            elif deform_type == 'WAVE':
                mod = obj.modifiers.new(name="Wave", type='WAVE')
                mod.use_x = deform.get('use_x', True)
                mod.use_y = deform.get('use_y', True)
                mod.height = deform.get('height', 0.5)
                mod.width = deform.get('width', 1.5)
                mod.speed = deform.get('speed', 0.25)
                mod.narrowness = deform.get('narrowness', 1.5)
    
    def _apply_modifiers(self, obj_name: str, params: Dict[str, Any]):
        """Apply modifiers based on parameters"""
        obj = bpy.data.objects[obj_name]
        modifiers = params.get('modifiers', {})
        
        for mod_type, mod_params in modifiers.items():
            if mod_type == 'subdivision':
                mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
                mod.levels = mod_params.get('levels', 2)
            
            elif mod_type == 'bevel':
                mod = obj.modifiers.new(name="Bevel", type='BEVEL')
                mod.width = mod_params.get('width', 0.1)
                mod.segments = mod_params.get('segments', 3)
    
    def _export_mesh(self, filepath: Union[str, Path], format: str = 'STL'):
        """Export the current scene to the specified format"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if format.upper() == 'STL':
            bpy.ops.export_mesh.stl(
                filepath=str(filepath),
                use_selection=True
            )
        elif format.upper() == 'OBJ':
            bpy.ops.export_scene.obj(
                filepath=str(filepath),
                use_selection=True
            )
    

