from __future__ import annotations

from pathlib import Path

from ingestion.text_parser import TextParser
from ingestion.image_processor import ImageProcessor
from ingestion.video_processor import VideoProcessor
from retriever.web_search import WebSearch
from retriever.github_fetcher import GitHubFetcher
from retriever.reddit_fetcher import RedditFetcher
from cad_export.exporters import Exporters

try:
    from generator.blender_pipeline import BlenderPipeline as _RealBlenderPipeline
    BLENDER_AVAILABLE = True
except ImportError:
    from generator.model_interface import ModelInterface

    BLENDER_AVAILABLE = False

    class _RealBlenderPipeline(ModelInterface):
        """Placeholder pipeline when Blender bindings are unavailable."""

        def __init__(self) -> None:
            self.using_placeholder = True
            self.temp_dir = Path("temp")
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self._placeholder_stl = self.temp_dir / "placeholder_model.stl"

        def generate_model(self, description, images=None, videos=None, links=None):
            if not self._placeholder_stl.exists():
                self._placeholder_stl.write_text(
                    "solid placeholder_model\nendsolid placeholder_model\n",
                    encoding="utf-8"
                )
            return str(self._placeholder_stl)

        def fetch_additional_data(self, description):
            return {}

        def validate_input(self, description, images=None, videos=None, links=None):
            return True

        def export_model(self, format_type):
            return str(self._placeholder_stl)

BlenderPipeline = _RealBlenderPipeline


class Pipeline:
    def __init__(self):
        self.text_parser = TextParser()
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.web_search = WebSearch()
        self.github_fetcher = GitHubFetcher()
        self.reddit_fetcher = RedditFetcher()
        self.blender_pipeline = BlenderPipeline()
        self.exporters = Exporters()
        self.blender_available = BLENDER_AVAILABLE

        if not BLENDER_AVAILABLE:
            print("[pipeline] Blender module not found. Running in placeholder generation mode.")

    def run(self, input_data):
        # Ingest input data
        if isinstance(input_data, str):
            parsed_data = self.text_parser.parse_text(input_data)
        elif isinstance(input_data, bytes):
            parsed_data = self.image_processor.process_image(input_data)
        elif isinstance(input_data, list):
            parsed_data = self.video_processor.process_video(input_data)
        else:
            raise ValueError("Unsupported input data type")

        # Retrieve additional data
        web_results = self.web_search.search_web(parsed_data)
        github_data = self.github_fetcher.fetch_repositories(parsed_data)
        reddit_data = self.reddit_fetcher.fetch_posts(parsed_data)

        # Generate 3D model
        model = self.blender_pipeline.generate_model(parsed_data, web_results, github_data, reddit_data)

        # Export model to CAD format
        step_file = self.exporters.export_to_step(model)
        obj_file = self.exporters.export_to_obj(model)

        return step_file, obj_file
