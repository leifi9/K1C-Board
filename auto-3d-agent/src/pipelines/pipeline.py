from ..ingestion.text_parser import TextParser
from ..ingestion.image_processor import ImageProcessor
from ..ingestion.video_processor import VideoProcessor
from ..retriever.web_search import WebSearch
from ..retriever.github_fetcher import GitHubFetcher
from ..retriever.reddit_fetcher import RedditFetcher
from ..generator.blender_pipeline import BlenderPipeline
from ..cad_export.exporters import Exporters

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