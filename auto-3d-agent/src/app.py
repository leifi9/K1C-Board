from .ingestion.text_parser import TextParser
from .ingestion.image_processor import ImageProcessor
from .ingestion.video_processor import VideoProcessor
from .retriever.web_search import WebSearch
from .retriever.github_fetcher import GitHubFetcher
from .retriever.reddit_fetcher import RedditFetcher
from .generator.blender_pipeline import BlenderPipeline
from .cad_export.exporters import Exporters
from .pipelines.pipeline import Pipeline

def main():
    # Initialize components
    text_parser = TextParser()
    image_processor = ImageProcessor()
    video_processor = VideoProcessor()
    web_search = WebSearch()
    github_fetcher = GitHubFetcher()
    reddit_fetcher = RedditFetcher()
    blender_pipeline = BlenderPipeline()
    exporters = Exporters()

    # Orchestrate the workflow
    # Example: ingest input, retrieve data, generate model, export
    input_data = "Your input description here"
    parsed_text = text_parser.parse_text(input_data)
    keywords = text_parser.extract_keywords(parsed_text)

    # Further processing and retrieval can be added here

    # Generate and export the 3D model
    model = blender_pipeline.generate_model(input_data)
    exporters.export_to_step(model, "output.step")

if __name__ == "__main__":
    main()