# TODO: Fix auto-3d-agent bugs and integrate into K1C-Board

1. [x] Update auto-3d-agent/requirements.txt to note Blender and FreeCAD installation requirements.
2. [x] Fix auto-3d-agent/tests/test_generator.py: change assertion to check for string path return.
3. [x] Improve auto-3d-agent/src/ingestion/text_parser.py with better keyword extraction.
4. [x] Create cross-platform run script (run_agent.bat for Windows).
5. [x] Update main README.md to describe K1C-Board as a platform for AI agents.
6. [x] Update AGENTS.md to list available agents.
7. [x] Fix import issues in app.py and pipeline.py for relative imports.
8. [x] Make retriever classes return empty data instead of crashing.
9. [x] Add fallback for FreeCAD in export_to_cad.
10. [x] Improve VideoProcessor and other stubs.
11. [x] Create missing parametric_shapes.py module with GearShape, SpringShape, and ThreadShape.
12. [x] Add missing __init__.py files (src/, src/utils/, src/pipelines/).
13. [x] Implement Exporters class methods (export_to_step, export_to_obj) with FreeCAD and fallback.
14. [x] Implement ImageProcessor methods (process_image, extract_features) with OpenCV.
15. [x] Implement VideoProcessor methods (process_video, extract_frames, extract_key_frames).
16. [x] Implement WebSearch methods with DuckDuckGo HTML search and BeautifulSoup.
17. [x] Implement RedditFetcher methods with Reddit JSON API.
18. [x] Complete BlenderPipeline TODO items (process_input_images, process_input_videos, process_input_links).
19. [x] Add missing _update_params_from_features method.
20. [x] Verify all Python files compile successfully.
21. [ ] Install Python dependencies (requires network connectivity).
22. [ ] Install Blender, FreeCAD on the system (requires user action).
23. [ ] Run unit tests to verify fixes (requires dependencies installed).
24. [ ] Run examples to test functionality (requires Blender).
25. [ ] Test full pipeline (requires all dependencies).
