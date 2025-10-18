"""
Mock bpy module for testing when Blender is not installed.
This provides minimal functionality to allow tests to import and run.
"""

class MockObject:
    def __init__(self, name="MockObject"):
        self.name = name
        self.scale = (1.0, 1.0, 1.0)
        self.location = (0.0, 0.0, 0.0)
        self.rotation_euler = (0.0, 0.0, 0.0)
        self.modifiers = MockModifiers()
        
class MockModifiers:
    def __init__(self):
        self.modifiers = []
    
    def new(self, name, type):
        mod = MockModifier(name, type)
        self.modifiers.append(mod)
        return mod

class MockModifier:
    def __init__(self, name, mod_type):
        self.name = name
        self.type = mod_type
        # Common modifier properties
        self.levels = 2
        self.width = 0.1
        self.segments = 3
        self.use_axis = [True, False, False]
        self.use_clip = False
        self.object = None
        self.operation = 'DIFFERENCE'
        self.deform_method = 'BEND'
        self.angle = 0
        self.factor = 1.0
        self.deform_axis = 'X'
        self.use_x = True
        self.use_y = True
        self.height = 0.5
        self.speed = 0.25
        self.narrowness = 1.5

class MockMesh:
    def __init__(self, name="MockMesh"):
        self.name = name
    
    def from_pydata(self, vertices, edges, faces):
        self.vertices = vertices
        self.edges = edges
        self.faces = faces
    
    def update(self):
        pass

class MockData:
    def __init__(self):
        self.objects = MockDataObjects()
        self.meshes = MockDataMeshes()
    
class MockDataObjects:
    def __init__(self):
        self._objects = {}
    
    def new(self, name, data):
        obj = MockObject(name)
        self._objects[name] = obj
        return obj
    
    def __getitem__(self, key):
        if key not in self._objects:
            self._objects[key] = MockObject(key)
        return self._objects[key]

class MockDataMeshes:
    def new(self, name):
        return MockMesh(name)

class MockCollection:
    def __init__(self):
        self.objects = MockCollectionObjects()

class MockCollectionObjects:
    def link(self, obj):
        pass

class MockScene:
    def __init__(self):
        self.collection = MockCollection()

class MockContext:
    def __init__(self):
        self.active_object = MockObject()
        self.scene = MockScene()

class MockOps:
    def __init__(self):
        self.object = MockOpsObject()
        self.mesh = MockOpsMesh()
        self.export_mesh = MockOpsExportMesh()
        self.export_scene = MockOpsExportScene()
        self.import_mesh = MockOpsImportMesh()
        self.import_scene = MockOpsImportScene()

class MockOpsObject:
    def select_all(self, action='SELECT'):
        pass
    
    def delete(self):
        pass
    
    def add(self, type='MESH', enter_editmode=False):
        pass

class MockOpsMesh:
    def primitive_cube_add(self):
        pass
    
    def primitive_uv_sphere_add(self, segments=32, ring_count=16):
        pass
    
    def primitive_cylinder_add(self, vertices=32):
        pass
    
    def primitive_cone_add(self, vertices=32):
        pass
    
    def primitive_torus_add(self, major_segments=48, minor_segments=24, 
                           major_radius=1.0, minor_radius=0.25):
        pass

class MockOpsExportMesh:
    def stl(self, filepath, use_selection=True):
        # Create a dummy file
        from pathlib import Path
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).touch()

class MockOpsExportScene:
    def obj(self, filepath, use_selection=True):
        # Create a dummy file
        from pathlib import Path
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).touch()

class MockOpsImportMesh:
    def stl(self, filepath):
        pass

class MockOpsImportScene:
    def obj(self, filepath):
        pass

# Create module-level objects
data = MockData()
context = MockContext()
ops = MockOps()
