# 3D Printing Adapter Expert System

## Overview
This system specializes in creating **3D printing adapters and modification parts** from dual CAD inputs.

## Features
- **Dual CAD Processing**: Takes two CAD files and creates connecting adapters
- **3D Printing Optimization**: Optimizes geometry for FDM/SLA printing
- **Material-Aware**: Applies proper tolerances for PLA, PETG, ABS, TPU
- **STL Export**: Generates print-ready STL files with validation
- **Modification Parts**: Creates upgrade and modification components

## Quick Start

### Installation
```bash
cd K1C-Board/auto-3d-agent
pip install -r requirements.txt
```

### Basic Usage

#### Create an Adapter Between Two Parts
```bash
python src/app.py --mode dual-cad \
  --input1 part1.step \
  --input2 part2.step \
  --material PLA \
  --tolerance normal \
  --output my_adapter
```

#### Create a Modification Part
```bash
python src/app.py --mode modification \
  --input1 base_part.step \
  --material PETG \
  --output upgrade_bracket
```

#### Generate Sample Adapter
```bash
python src/app.py --mode sample
```

## Architecture

### Components
- **CAD Processor** (`ingestion/cad_processor.py`): Dual CAD input analysis
- **Adapter Generator** (`generator/adapter_generator.py`): Blender-based 3D modeling
- **STL Exporter** (`cad_export/stl_exporter.py`): Print-ready file export
- **Main App** (`app.py`): Workflow orchestration

### Workflow
1. Load and validate two CAD files
2. Detect connection interfaces
3. Calculate adapter geometry with tolerances
4. Generate 3D model using Blender
5. Optimize for 3D printing
6. Export STL with validation
7. Generate assembly report

## Supported Formats

### Input
- STEP (.step, .stp)
- STL (.stl)
- OBJ (.obj)
- PLY (.ply)

### Output
- STL (Binary/ASCII)
- OBJ
- 3MF (if available)

## Materials & Tolerances

### Supported Materials
- **PLA**: Standard, easy to print (200°C)
- **PETG**: Strong, heat-resistant (235°C)
- **ABS**: Durable, higher shrinkage (240°C)
- **TPU**: Flexible, requires special handling

### Tolerance Classes
- **loose**: 0.3mm clearance (slip fit)
- **normal**: 0.2mm clearance (standard)
- **tight**: 0.1mm clearance (close fit)
- **press-fit**: -0.05mm interference

## Examples

### Example 1: Camera Mount Adapter
```bash
python src/app.py --mode dual-cad \
  --input1 camera_mount.step \
  --input2 tripod_plate.step \
  --material PLA \
  --output camera_adapter
```

### Example 2: Reinforcement Bracket
```bash
python src/app.py --mode modification \
  --input1 weak_joint.step \
  --material PETG \
  --output reinforcement
```

## Output Files

For each adapter creation, you'll get:
- `adapter_name.stl` - 3D printable file
- `adapter_name_metadata.json` - Print recommendations
- `adapter_name_report.json` - Full analysis and specs

## Requirements

### Python Dependencies
- numpy
- Blender Python API (bpy)
- trimesh / Open3D (for CAD processing)

### Optional
- FreeCAD Python API
- OpenSCAD

## Troubleshooting

### "CAD file not found"
Ensure file paths are absolute or relative to working directory.

### "Unsupported file format"
Check that input files are STEP, STL, OBJ, or PLY format.

### "Geometry validation failed"
Input CAD may have non-manifold geometry. Try repairing in CAD software first.

## Contributing
This is part of the Grounddata 3D Config App ecosystem.

## License
MIT License - See LICENSE file for details
