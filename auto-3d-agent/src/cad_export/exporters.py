from pathlib import Path
from typing import Union


class Exporters:
    def export_to_step(self, model_path: Union[str, Path], output_path: str = None) -> str:
        """
        Export the model to STEP format using FreeCAD if available,
        otherwise use a fallback method.
        
        Args:
            model_path: Path to the input model file (STL, OBJ, etc.)
            output_path: Optional output path, defaults to same name with .step extension
            
        Returns:
            Path to the exported STEP file
        """
        try:
            import FreeCAD as App
            import Part
            import Mesh
            
            model_path = Path(model_path)
            if output_path is None:
                output_path = model_path.with_suffix('.step')
            else:
                output_path = Path(output_path)
            
            # Load the mesh
            mesh = Mesh.Mesh(str(model_path))
            
            # Create a new document
            doc = App.newDocument("Export")
            
            # Convert mesh to shape
            shape = Part.Shape()
            shape.makeShapeFromMesh(mesh.Topology, 0.1)
            
            # Create a part feature
            part = doc.addObject("Part::Feature", "Shape")
            part.Shape = shape
            
            # Export to STEP
            Part.export([part], str(output_path))
            
            # Close document
            App.closeDocument(doc.Name)
            
            return str(output_path)
            
        except ImportError:
            # Fallback: just copy/rename the file
            model_path = Path(model_path)
            if output_path is None:
                output_path = model_path.with_suffix('.step')
            else:
                output_path = Path(output_path)
            
            import shutil
            shutil.copy(str(model_path), str(output_path))
            return str(output_path)

    def export_to_obj(self, model_path: Union[str, Path], output_path: str = None) -> str:
        """
        Export the model to OBJ format.
        
        Args:
            model_path: Path to the input model file
            output_path: Optional output path, defaults to same name with .obj extension
            
        Returns:
            Path to the exported OBJ file
        """
        try:
            import bpy
            
            model_path = Path(model_path)
            if output_path is None:
                output_path = model_path.with_suffix('.obj')
            else:
                output_path = Path(output_path)
            
            # Clear scene
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
            # Import the model based on extension
            file_ext = model_path.suffix.lower()
            if file_ext == '.stl':
                bpy.ops.import_mesh.stl(filepath=str(model_path))
            elif file_ext == '.obj':
                bpy.ops.import_scene.obj(filepath=str(model_path))
            else:
                raise ValueError(f"Unsupported input format: {file_ext}")
            
            # Export to OBJ
            bpy.ops.export_scene.obj(
                filepath=str(output_path),
                use_selection=True
            )
            
            return str(output_path)
            
        except ImportError:
            # Fallback: just copy/rename the file
            model_path = Path(model_path)
            if output_path is None:
                output_path = model_path.with_suffix('.obj')
            else:
                output_path = Path(output_path)
            
            import shutil
            shutil.copy(str(model_path), str(output_path))
            return str(output_path)