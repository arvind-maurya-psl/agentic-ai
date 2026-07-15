"""
Conftest for pytest configuration and shared fixtures.

Provides mocks and fixtures for testing the agentic AI application.
"""

import json
import os

from unittest.mock import MagicMock

import pytest


# Set deterministic test defaults for runtime configuration.
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")


@pytest.fixture
def mock_bedrock_client():
    """Create a mock Bedrock client."""
    return MagicMock()


@pytest.fixture
def mock_bedrock_response():
    """Create a mock Bedrock response."""
    return {
        "body": MagicMock(
            read=MagicMock(
                return_value=json.dumps({
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a mock response from Bedrock Claude model.",
                        }
                    ],
                    "usage": {
                        "input_tokens": 100,
                        "output_tokens": 50,
                    },
                }).encode("utf-8")
            )
        ),
        "ResponseMetadata": {
            "HTTPStatusCode": 200,
        },
    }


@pytest.fixture
def mock_bedrock_streaming_response():
    """Create a mock Bedrock streaming response."""

    def mock_stream_events():
        chunks = [
            {"chunk": {"bytes": json.dumps({
                "type": "content_block_delta",
                "delta": {"type": "text_delta", "text": "Hello "},
            }).encode("utf-8")}},
            {"chunk": {"bytes": json.dumps({
                "type": "content_block_delta",
                "delta": {"type": "text_delta", "text": "from "},
            }).encode("utf-8")}},
            {"chunk": {"bytes": json.dumps({
                "type": "content_block_delta",
                "delta": {"type": "text_delta", "text": "Bedrock."},
            }).encode("utf-8")}},
        ]
        return iter(chunks)

    return {
        "body": mock_stream_events(),
    }


@pytest.fixture
def bedrock_service_mock(mock_bedrock_client):
    """Create a mock BedrockService."""
    from agentic_ai.services import BedrockService

    with pytest.mock.patch.object(
        BedrockService, "_create_client", return_value=mock_bedrock_client
    ):
        service = BedrockService()
        return service


@pytest.fixture
def sample_messages():
    """Create sample messages for testing."""
    return [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
        {"role": "user", "content": "Can you help me with Python?"},
    ]


@pytest.fixture
def sample_task():
    """Create a sample agent task."""
    from agentic_ai.agents import AgentTask

    return AgentTask(
        task_id="test-task-001",
        description="Analyze sales data for Q3",
        objective="Identify key trends and patterns",
        context={"department": "sales", "quarter": "Q3"},
    )


@pytest.fixture
def app():
    """Create an application instance for testing."""
    from agentic_ai.app import AgenticAIApplication

    return AgenticAIApplication()
