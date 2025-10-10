import unittest
from src.ingestion.text_parser import TextParser
from src.ingestion.image_processor import ImageProcessor
from src.ingestion.video_processor import VideoProcessor

class TestIngestion(unittest.TestCase):

    def setUp(self):
        self.text_parser = TextParser()
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()

    def test_parse_text(self):
        input_text = "This is a sample text for testing."
        parsed_text = self.text_parser.parse_text(input_text)
        self.assertIsNotNone(parsed_text)
        self.assertIn("sample", parsed_text)

    def test_extract_keywords(self):
        input_text = "This is a sample text for testing keyword extraction."
        keywords = self.text_parser.extract_keywords(input_text)
        self.assertGreater(len(keywords), 0)

    def test_process_image(self):
        image_path = "path/to/sample/image.jpg"
        features = self.image_processor.process_image(image_path)
        self.assertIsNotNone(features)

    def test_extract_features(self):
        image_path = "path/to/sample/image.jpg"
        features = self.image_processor.extract_features(image_path)
        self.assertGreater(len(features), 0)

    def test_process_video(self):
        video_path = "path/to/sample/video.mp4"
        frames = self.video_processor.process_video(video_path)
        self.assertIsNotNone(frames)

    def test_extract_frames(self):
        video_path = "path/to/sample/video.mp4"
        frames = self.video_processor.extract_frames(video_path)
        self.assertGreater(len(frames), 0)

if __name__ == '__main__':
    unittest.main()