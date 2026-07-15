"""Unit tests for plugins."""

import pytest

from agentic_ai.plugins.calculator import CalculatorPlugin
from agentic_ai.plugins.data_analysis import DataAnalysisPlugin


class TestCalculatorPlugin:
    """Tests for CalculatorPlugin."""

    def test_add(self):
        """Test addition."""
        result = CalculatorPlugin.add(5, 3)
        assert result == 8

    def test_subtract(self):
        """Test subtraction."""
        result = CalculatorPlugin.subtract(10, 4)
        assert result == 6

    def test_multiply(self):
        """Test multiplication."""
        result = CalculatorPlugin.multiply(6, 7)
        assert result == 42

    def test_divide(self):
        """Test division."""
        result = CalculatorPlugin.divide(10, 2)
        assert result == 5

    def test_divide_by_zero(self):
        """Test division by zero error."""
        with pytest.raises(ValueError):
            CalculatorPlugin.divide(10, 0)

    def test_power(self):
        """Test exponentiation."""
        result = CalculatorPlugin.power(2, 3)
        assert result == 8

    def test_square_root(self):
        """Test square root."""
        result = CalculatorPlugin.square_root(16)
        assert result == 4.0

    def test_square_root_negative(self):
        """Test square root of negative number."""
        with pytest.raises(ValueError):
            CalculatorPlugin.square_root(-4)


class TestDataAnalysisPlugin:
    """Tests for DataAnalysisPlugin."""

    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        result = DataAnalysisPlugin.analyze_sentiment("This is great!")
        assert "sentiment" in result
        assert "score" in result

    def test_extract_entities(self):
        """Test entity extraction."""
        result = DataAnalysisPlugin.extract_entities("John Smith works at Google")
        assert isinstance(result, list)

    def test_summarize_text(self):
        """Test text summarization."""
        text = "This is a long document with multiple paragraphs. " * 10
        result = DataAnalysisPlugin.summarize_text(text, num_sentences=3)
        assert isinstance(result, str)

    def test_statistical_summary(self):
        """Test statistical summary calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = DataAnalysisPlugin.statistical_summary(data)

        assert result["min"] == 1
        assert result["max"] == 10
        assert result["mean"] == 5.5
        assert result["count"] == 10

    def test_statistical_summary_empty(self):
        """Test statistical summary with empty data."""
        result = DataAnalysisPlugin.statistical_summary([])
        assert "error" in result
