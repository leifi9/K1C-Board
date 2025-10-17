"""
Tests for the data ingestion module.

These tests verify the functionality of text parsing, image processing,
and video processing components.
"""

import unittest
from src.ingestion.text_parser import TextParser
from src.ingestion.image_processor import ImageProcessor
from src.ingestion.video_processor import VideoProcessor


class TestIngestion(unittest.TestCase):
    """Test cases for data ingestion components."""

    def setUp(self):
        """Set up test fixtures."""
        self.text_parser = TextParser()
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()

    def test_parse_text(self):
        """Test that parse_text returns the input text."""
        input_text = "This is a sample text for testing."
        parsed_text = self.text_parser.parse_text(input_text)
        self.assertIsNotNone(parsed_text)
        self.assertIn("sample", parsed_text)

    def test_extract_keywords(self):
        """Test that extract_keywords returns a list of keywords."""
        input_text = "This is a sample text for testing keyword extraction."
        keywords = self.text_parser.extract_keywords(input_text)
        self.assertIsNotNone(keywords)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        # Check that common words are filtered out
        self.assertIn("sample", keywords)
        self.assertIn("testing", keywords)
        self.assertIn("keyword", keywords)
        self.assertIn("extraction", keywords)

    def test_extract_parameters(self):
        """Test parameter extraction from text."""
        input_text = "Create a gear with 20 teeth and 5mm module"
        params = self.text_parser.extract_parameters(input_text)
        self.assertIsNotNone(params)
        self.assertIsInstance(params, dict)

    def test_process_image(self):
        """Test that process_image returns a dict (even if empty for stub)."""
        image_path = "path/to/sample/image.jpg"
        features = self.image_processor.process_image(image_path)
        self.assertIsNotNone(features)
        self.assertIsInstance(features, dict)

    def test_extract_features(self):
        """Test that extract_features returns a list (empty for stub implementation)."""
        image_path = "path/to/sample/image.jpg"
        features = self.image_processor.extract_features(image_path)
        self.assertIsNotNone(features)
        self.assertIsInstance(features, list)
        # Note: Current implementation returns empty list as it's a stub

    def test_process_video(self):
        """Test that process_video returns a list (even if empty for stub)."""
        video_path = "path/to/sample/video.mp4"
        frames = self.video_processor.process_video(video_path)
        self.assertIsNotNone(frames)
        self.assertIsInstance(frames, list)

    def test_extract_frames(self):
        """Test that extract_frames returns a list (empty for stub implementation)."""
        video_path = "path/to/sample/video.mp4"
        frames = self.video_processor.extract_frames(video_path)
        self.assertIsNotNone(frames)
        self.assertIsInstance(frames, list)
        # Note: Current implementation returns empty list as it's a stub


if __name__ == '__main__':
    unittest.main()