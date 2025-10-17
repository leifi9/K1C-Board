# Example: Creating a cylindrical adapter

Run the following command:

```bash
python src/app.py --mode dual-cad \
  --input1 examples/shaft_8mm.step \
  --input2 examples/hole_6mm.step \
  --material PLA \
  --tolerance normal \
  --output shaft_adapter
```

This will create an adapter that connects:
- An 8mm diameter shaft
- To a 6mm diameter hole
- Using PLA material with 0.2mm tolerance
- Optimized for 3D printing

Output includes:
- shaft_adapter.stl (ready for slicing)
- shaft_adapter_report.json (specifications)
- shaft_adapter_metadata.json (print settings)
