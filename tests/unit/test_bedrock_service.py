"""Unit tests for BedrockService."""

import json
from unittest.mock import MagicMock, patch

import pytest

from agentic_ai.services.bedrock_service import (
    BedrockModelError,
    BedrockService,
    BedrockServiceError,
)


class TestBedrockService:
    """Tests for BedrockService."""

    def test_initialization(self):
        """Test BedrockService initialization."""
        with patch("boto3.client") as mock_boto:
            service = BedrockService()
            assert service.model_id is not None
            assert service.region is not None
            mock_boto.assert_called_once()

    def test_invoke_model_success(self, mock_bedrock_client, mock_bedrock_response):
        """Test successful model invocation."""
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response

        with patch("boto3.client", return_value=mock_bedrock_client):
            service = BedrockService()
            response = service.invoke_model(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1024,
                temperature=0.7,
            )

            assert response == "This is a mock response from Bedrock Claude model."
            mock_bedrock_client.invoke_model.assert_called_once()

    def test_invoke_model_with_system_prompt(
        self, mock_bedrock_client, mock_bedrock_response
    ):
        """Test model invocation with system prompt."""
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response

        with patch("boto3.client", return_value=mock_bedrock_client):
            service = BedrockService()
            response = service.invoke_model(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1024,
                temperature=0.7,
                system_prompt="You are a helpful assistant.",
            )

            assert response is not None
            call_args = mock_bedrock_client.invoke_model.call_args
            body = json.loads(call_args[1]["body"])
            assert body["system"] == "You are a helpful assistant."

    def test_invoke_model_temperature_clamping(
        self, mock_bedrock_client, mock_bedrock_response
    ):
        """Test temperature value clamping."""
        mock_bedrock_client.invoke_model.return_value = mock_bedrock_response

        with patch("boto3.client", return_value=mock_bedrock_client):
            service = BedrockService()
            
            # Test temperature > 2 clamped to 2
            service.invoke_model(
                messages=[{"role": "user", "content": "Hello"}],
                temperature=3.5,
            )
            
            call_args = mock_bedrock_client.invoke_model.call_args
            body = json.loads(call_args[1]["body"])
            assert body["temperature"] == 2

            # Reset mock
            mock_bedrock_client.reset_mock()
            mock_bedrock_client.invoke_model.return_value = mock_bedrock_response

            # Test negative temperature clamped to 0
            service.invoke_model(
                messages=[{"role": "user", "content": "Hello"}],
                temperature=-0.5,
            )
            
            call_args = mock_bedrock_client.invoke_model.call_args
            body = json.loads(call_args[1]["body"])
            assert body["temperature"] == 0

    def test_invoke_model_streaming(
        self, mock_bedrock_client, mock_bedrock_streaming_response
    ):
        """Test streaming model invocation."""
        mock_bedrock_client.invoke_model_with_response_stream.return_value = (
            mock_bedrock_streaming_response
        )

        with patch("boto3.client", return_value=mock_bedrock_client):
            service = BedrockService()
            
            response_chunks = list(
                service.invoke_model_streaming(
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=1024,
                )
            )

            assert len(response_chunks) > 0
            full_response = "".join(response_chunks)
            assert "Hello" in full_response

    def test_invoke_model_empty_response(self, mock_bedrock_client):
        """Test handling of empty Bedrock response."""
        mock_bedrock_client.invoke_model.return_value = {
            "body": MagicMock(
                read=MagicMock(
                    return_value=json.dumps({
                        "content": [],
                    }).encode("utf-8")
                )
            )
        }

        with patch("boto3.client", return_value=mock_bedrock_client):
            service = BedrockService()
            response = service.invoke_model(
                messages=[{"role": "user", "content": "Hello"}]
            )

            assert response == ""

    def test_get_model_info(self):
        """Test getting model information."""
        with patch("boto3.client"):
            service = BedrockService(region="us-west-2", model_id="test-model-123")
            info = service.get_model_info()

            assert info["region"] == "us-west-2"
            assert info["model_id"] == "test-model-123"
