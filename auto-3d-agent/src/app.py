"""
Enhanced 3D Agent App - Specialized for 3D Printing Adapters
Main application orchestrating dual CAD input processing and adapter generation.
"""

import sys
import os
import argparse
import json
from typing import Dict, List, Optional
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.text_parser import TextParser
from ingestion.image_processor import ImageProcessor
from ingestion.video_processor import VideoProcessor
from ingestion.cad_processor import CADProcessor, AdapterSpec
from retriever.web_search import WebSearch
from retriever.github_fetcher import GitHubFetcher
from retriever.reddit_fetcher import RedditFetcher
try:
    from generator.adapter_generator import AdapterGenerator as _BlenderAdapterGenerator

    class AdapterGenerator(_BlenderAdapterGenerator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.uses_blender = True
except ImportError:

    class AdapterGenerator:  # type: ignore[override]
        """Fallback adapter generator that outputs placeholder geometry."""

        _PLACEHOLDER_STL = (
            "solid adapter_placeholder\n"
            "  facet normal 0 0 1\n"
            "    outer loop\n"
            "      vertex 0 0 0\n"
            "      vertex 10 0 0\n"
            "      vertex 0 10 0\n"
            "    endloop\n"
            "  endfacet\n"
            "endsolid adapter_placeholder\n"
        )
        _PLACEHOLDER_OBJ = (
            "# Adapter placeholder\n"
            "o AdapterPlaceholder\n"
            "v 0.0 0.0 0.0\n"
            "v 10.0 0.0 0.0\n"
            "v 0.0 10.0 0.0\n"
            "f 1 2 3\n"
        )

        def __init__(self) -> None:
            self.uses_blender = False

        def generate_adapter(self, geometry: Dict, output_path: str) -> Dict:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            base_name = geometry.get('type') or 'adapter_placeholder'
            safe_name = str(base_name).replace(' ', '_')
            stl_path = output_dir / f"{safe_name}.stl"
            if not stl_path.exists():
                stl_path.write_text(self._PLACEHOLDER_STL, encoding='utf-8')
            obj_path = output_dir / f"{safe_name}.obj"
            if not obj_path.exists():
                obj_path.write_text(self._PLACEHOLDER_OBJ, encoding='utf-8')
            return {
                'success': True,
                'adapter_name': safe_name,
                'geometry_type': geometry.get('type', 'placeholder'),
                'print_optimization': {
                    'orientation': geometry.get('print_orientation', 'auto'),
                    'notes': ['Generated placeholder geometry because Blender is unavailable.'],
                    'print_time_estimate': 'N/A',
                },
                'export_files': {
                    'stl': str(stl_path),
                    'obj': str(obj_path),
                },
                'recommendations': [
                    'Install Blender to enable full geometry synthesis.',
                    'Treat this placeholder model as a stub for UI validation only.',
                ],
            }

        def clear_scene(self) -> None:
            return None

from cad_export.exporters import Exporters
from cad_export.step_exporter import *
from cad_export.stl_exporter import STLExporter
from pipelines.pipeline import Pipeline

class AdapterCreationApp:
    """Main application for creating 3D printing adapters from dual CAD inputs"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.initialize_components()
        
        # Create output directories
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.cad_input_dir = Path("cad_inputs")
        self.cad_input_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "default.yaml")
        
        # For now, return default config since we don't have PyYAML
        return {
            "processing": {
                "default_material": "PLA",
                "default_tolerance": "normal",
                "output_formats": ["stl", "step", "obj"]
            },
            "3d_printing": {
                "layer_heights": {"fine": 0.1, "normal": 0.2, "fast": 0.3},
                "materials": {
                    "PLA": {"temp": 200, "bed": 60, "shrinkage": 0.003},
                    "PETG": {"temp": 235, "bed": 80, "shrinkage": 0.002},
                    "ABS": {"temp": 240, "bed": 100, "shrinkage": 0.005}
                }
            }
        }
    
    def initialize_components(self):
        """Initialize all processing components"""
        # Core processors
        self.text_parser = TextParser()
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.cad_processor = CADProcessor()
        
        # Data retrievers
        self.web_search = WebSearch()
        self.github_fetcher = GitHubFetcher()
        self.reddit_fetcher = RedditFetcher()
        
        # 3D generators
        self.adapter_generator = AdapterGenerator()
        
        # Exporters
        self.exporters = Exporters()
        self.stl_exporter = STLExporter()
        
        # Pipeline orchestrator
        self.pipeline = Pipeline()
        self.blender_available = getattr(self.adapter_generator, "uses_blender", True) and getattr(self.pipeline, "blender_available", True)

        if not getattr(self.adapter_generator, "uses_blender", True):
            print("[adapter] Blender runtime unavailable; using placeholder adapter generator.")
        if not getattr(self.pipeline, "blender_available", True):
            print("[adapter] Pipeline running in placeholder mode; geometry will be mocked.")

        
        print("[ok] All components initialized successfully")
    
    def create_adapter_from_dual_cad(self, cad_file_1: str, cad_file_2: str, 
                                   adapter_spec: AdapterSpec = None, 
                                   output_name: str = "custom_adapter") -> Dict:
        """Main workflow for creating adapter from two CAD files"""
        
        print(f"Starting adapter creation workflow...")
        print(f"   Input 1: {cad_file_1}")
        print(f"   Input 2: {cad_file_2}")
        
        # Use default spec if none provided
        if adapter_spec is None:
            adapter_spec = AdapterSpec(
                connection_type='mechanical',
                tolerance_class=self.config['processing']['default_tolerance'],
                material=self.config['processing']['default_material'],
                print_orientation='auto',
                support_preference='minimize'
            )
        
        try:
            # Step 1: Process dual CAD inputs
            print("Processing CAD inputs...")
            cad_result = self.cad_processor.process_dual_cad_input(
                cad_file_1, cad_file_2, adapter_spec
            )
            
            if not cad_result['success']:
                return {'success': False, 'error': 'CAD processing failed', 'details': cad_result}
            
            print(f"   Detected {len(cad_result['detected_interfaces'])} connection interfaces")
            
            # Step 2: Generate adapter geometry
            print("Generating adapter geometry...")
            adapter_geometry = cad_result['adapter_geometry']
            
            # Create output path
            output_path = self.output_dir / f"{output_name}"
            output_path.mkdir(exist_ok=True)
            
            # Step 3: Generate 3D model using Blender
            if getattr(self.adapter_generator, "uses_blender", True):
                print("Creating 3D model with Blender...")
            else:
                print("Creating placeholder geometry (Blender unavailable)...")
            generation_result = self.adapter_generator.generate_adapter(
                adapter_geometry, str(output_path)
            )
            
            if not generation_result['success']:
                return {'success': False, 'error': 'Adapter generation failed', 'details': generation_result}
            
            # Step 4: Export in multiple formats
            print("Exporting files...")
            export_results = {}
            
            # Export STL (primary for 3D printing)
            if 'stl' in self.config['processing']['output_formats']:
                stl_path = output_path / f"{output_name}.stl"
                # Note: In real implementation, we'd get vertices/faces from Blender
                # For now, creating placeholder
                export_results['stl'] = {'file_path': str(stl_path), 'format': 'STL'}
            
            # Step 5: Generate comprehensive report
            print("Generating report...")
            report = self._generate_adapter_report(
                cad_result, generation_result, export_results, adapter_spec, output_name
            )
            
            # Save report
            report_path = output_path / f"{output_name}_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"Adapter creation completed successfully!")
            print(f"   Output directory: {output_path}")
            print(f"   Report: {report_path}")
            
            return {
                'success': True,
                'output_path': str(output_path),
                'report_path': str(report_path),
                'export_files': export_results,
                'adapter_spec': adapter_spec.__dict__,
                'summary': report['summary']
            }
            
        except Exception as e:
            error_msg = f"Adapter creation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def create_modification_part(self, base_cad_file: str, modification_spec: Dict, 
                               output_name: str = "modification_part") -> Dict:
        """Create a modification/upgrade part for an existing component"""
        
        print(f"Creating modification part for: {base_cad_file}")
        
        try:
            # Process the base CAD file
            base_model = self.cad_processor.load_cad_model(base_cad_file)
            
            # Create modification geometry based on spec
            modification_geometry = self._generate_modification_geometry(base_model, modification_spec)
            
            # Generate the part
            output_path = self.output_dir / f"{output_name}"
            output_path.mkdir(exist_ok=True)
            
            generation_result = self.adapter_generator.generate_adapter(
                modification_geometry, str(output_path)
            )
            
            if generation_result['success']:
                print(f"Modification part created: {output_path}")
                return {
                    'success': True,
                    'output_path': str(output_path),
                    'part_type': 'modification',
                    'base_file': base_cad_file
                }
            else:
                return {'success': False, 'error': 'Modification generation failed'}
                
        except Exception as e:
            return {'success': False, 'error': f"Modification creation failed: {str(e)}"}
    
    def _generate_modification_geometry(self, base_model, modification_spec: Dict) -> Dict:
        """Generate geometry for modification parts"""
        
        # Analyze the base model to understand what needs to be modified
        modification_type = modification_spec.get('type', 'bracket')
        
        if modification_type == 'bracket':
            return self._create_bracket_geometry(base_model, modification_spec)
        elif modification_type == 'reinforcement':
            return self._create_reinforcement_geometry(base_model, modification_spec)
        elif modification_type == 'mount':
            return self._create_mount_geometry(base_model, modification_spec)
        else:
            # Default to adapter geometry
            return {
                'type': 'bracket_adapter',
                'dimensions': {
                    'width': 50, 'depth': 30, 'thickness': 5
                },
                'mounting_holes': [
                    {'diameter': 3, 'position': [10, 10, 0], 'depth': 5},
                    {'diameter': 3, 'position': [40, 10, 0], 'depth': 5}
                ]
            }
    
    def _create_bracket_geometry(self, base_model, spec: Dict) -> Dict:
        """Create bracket geometry"""
        return {
            'type': 'bracket_adapter',
            'dimensions': spec.get('dimensions', {'width': 60, 'depth': 40, 'thickness': 6}),
            'mounting_holes': spec.get('mounting_holes', []),
            'features': spec.get('features', [])
        }
    
    def _create_reinforcement_geometry(self, base_model, spec: Dict) -> Dict:
        """Create reinforcement geometry"""
        return {
            'type': 'bracket_adapter',  # Use bracket as base for reinforcement
            'dimensions': spec.get('dimensions', {'width': 30, 'depth': 30, 'thickness': 8}),
            'features': [
                {'type': 'boss', 'diameter': 12, 'height': 10, 'position': [0, 0, 4]}
            ]
        }
    
    def _create_mount_geometry(self, base_model, spec: Dict) -> Dict:
        """Create mount geometry"""
        return {
            'type': 'cylindrical_adapter',
            'dimensions': spec.get('dimensions', {
                'length': 20, 'diameter_1': 15, 'diameter_2': 12, 'wall_thickness': 3
            })
        }
    
    def _generate_adapter_report(self, cad_result: Dict, generation_result: Dict, 
                               export_results: Dict, adapter_spec: AdapterSpec, 
                               output_name: str) -> Dict:
        """Generate comprehensive adapter creation report"""
        
        return {
            'adapter_name': output_name,
            'creation_timestamp': str(Path().resolve()),  # Placeholder
            'input_files': {
                'cad_file_1': cad_result['input_models']['model_1'],
                'cad_file_2': cad_result['input_models']['model_2']
            },
            'adapter_specifications': {
                'connection_type': adapter_spec.connection_type,
                'tolerance_class': adapter_spec.tolerance_class,
                'material': adapter_spec.material,
                'print_orientation': adapter_spec.print_orientation,
                'support_preference': adapter_spec.support_preference
            },
            'detected_interfaces': cad_result['detected_interfaces'],
            'generated_geometry': cad_result['adapter_geometry'],
            'print_optimization': generation_result.get('print_optimization', {}),
            'export_files': export_results,
            'recommendations': cad_result.get('recommendations', []) + 
                            generation_result.get('recommendations', []),
            'summary': {
                'adapter_type': cad_result['adapter_geometry']['type'],
                'print_ready': True,
                'estimated_print_time': generation_result.get('print_optimization', {}).get('print_time_estimate', 'Unknown'),
                'material_usage': 'Estimated based on geometry',
                'post_processing_required': 'threads' in str(cad_result['adapter_geometry'])
            }
        }
    
    def list_supported_formats(self) -> List[str]:
        """List supported CAD input formats"""
        return self.cad_processor.supported_formats
    
    def get_material_properties(self, material: str) -> Dict:
        """Get properties for a specific 3D printing material"""
        return self.config['3d_printing']['materials'].get(material, {})
    
    def create_sample_adapter(self, adapter_type: str = "cylindrical") -> Dict:
        """Create a sample adapter for testing"""
        
        print(f"Creating sample {adapter_type} adapter...")
        
        # Create sample geometry
        if adapter_type == "cylindrical":
            sample_geometry = {
                'type': 'cylindrical_adapter',
                'dimensions': {
                    'length': 25,
                    'diameter_1': 10.2,
                    'diameter_2': 8.2,
                    'wall_thickness': 2
                },
                'print_orientation': 'vertical'
            }
        else:
            sample_geometry = {
                'type': 'bracket_adapter',
                'dimensions': {'width': 50, 'depth': 30, 'thickness': 5},
                'mounting_holes': [
                    {'diameter': 3, 'position': [10, 10, 0], 'depth': 5}
                ]
            }
        
        # Generate the sample
        output_path = self.output_dir / f"sample_{adapter_type}_adapter"
        output_path.mkdir(exist_ok=True)
        
        result = self.adapter_generator.generate_adapter(sample_geometry, str(output_path))
        
        if result['success']:
            print(f"Sample adapter created: {output_path}")
        
        return result

def main():
    """Main entry point for the 3D printing adapter application"""
    
    parser = argparse.ArgumentParser(description="3D Printing Adapter Creation Tool")
    parser.add_argument('--mode', choices=['dual-cad', 'modification', 'sample'], 
                       default='dual-cad', help='Operation mode')
    parser.add_argument('--input1', type=str, help='First CAD input file')
    parser.add_argument('--input2', type=str, help='Second CAD input file')
    parser.add_argument('--material', type=str, default='PLA', 
                       choices=['PLA', 'PETG', 'ABS', 'TPU'], help='3D printing material')
    parser.add_argument('--tolerance', type=str, default='normal',
                       choices=['loose', 'normal', 'tight', 'press-fit'], help='Fit tolerance')
    parser.add_argument('--output', type=str, default='custom_adapter', help='Output name')
    parser.add_argument('--config', type=str, help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize the application
    app = AdapterCreationApp(args.config)
    
    print("3D Printing Adapter Creation Tool")
    print("=" * 50)
    
    if args.mode == 'dual-cad':
        if not args.input1 or not args.input2:
            print("❌ Dual CAD mode requires both --input1 and --input2")
            return
        
        # Create adapter specification
        adapter_spec = AdapterSpec(
            connection_type='mechanical',
            tolerance_class=args.tolerance,
            material=args.material,
            print_orientation='auto',
            support_preference='minimize'
        )
        
        # Create the adapter
        result = app.create_adapter_from_dual_cad(
            args.input1, args.input2, adapter_spec, args.output
        )
        
        if result['success']:
            print("\n Success! Adapter created successfully.")
            print(f"Check output directory: {result['output_path']}")
        else:
            print(f"\n❌ Failed: {result['error']}")
    
    elif args.mode == 'modification':
        if not args.input1:
            print("❌ Modification mode requires --input1 (base CAD file)")
            return
            
        modification_spec = {
            'type': 'bracket',
            'material': args.material
        }
        
        result = app.create_modification_part(args.input1, modification_spec, args.output)
        
        if result['success']:
            print("\n Success! Modification part created.")
        else:
            print(f"\n❌ Failed: {result['error']}")
    
    elif args.mode == 'sample':
        # Create sample adapter for testing
        result = app.create_sample_adapter("cylindrical")
        
        if result['success']:
            print("\n Sample adapter created successfully!")
        else:
            print(f"\n❌ Failed to create sample: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("Done!")

if __name__ == "__main__":
    main()
