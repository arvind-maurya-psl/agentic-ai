"""Unit tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from agentic_ai.config import (
    AgentConfig,
    AppConfig,
    AWSConfig,
    SemanticKernelConfig,
    get_config,
    reset_config,
)


class TestAWSConfig:
    """Tests for AWSConfig."""

    def test_aws_config_defaults(self):
        """Test AWS config with defaults."""
        with patch.dict(os.environ, {"AWS_REGION": "us-east-1"}):
            config = AWSConfig()
            assert config.region == "us-east-1"
            assert config.max_retries == 3

    def test_aws_config_validation_missing_region(self):
        """Test AWS config validation fails without region."""
        config = AWSConfig(region="")
        with pytest.raises(ValueError):
            config.validate()

    def test_aws_config_from_env(self):
        """Test AWS config from environment."""
        with patch.dict(
            os.environ,
            {
                "AWS_REGION": "us-west-2",
                "BEDROCK_MODEL_ID": "custom-model",
                "AWS_MAX_RETRIES": "5",
            },
        ):
            config = AWSConfig()
            assert config.region == "us-west-2"
            assert config.bedrock_model_id == "custom-model"
            assert config.max_retries == 5


class TestSemanticKernelConfig:
    """Tests for SemanticKernelConfig."""

    def test_semantic_kernel_defaults(self):
        """Test Semantic Kernel config defaults."""
        config = SemanticKernelConfig()
        assert config.log_level == "INFO"
        assert config.log_enabled is True

    def test_semantic_kernel_validation_invalid_log_level(self):
        """Test validation with invalid log level."""
        config = SemanticKernelConfig(log_level="INVALID")
        with pytest.raises(ValueError):
            config.validate()

    def test_semantic_kernel_validation_valid_log_levels(self):
        """Test validation with valid log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config = SemanticKernelConfig(log_level=level)
            config.validate()  # Should not raise


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_agent_config_defaults(self):
        """Test agent config defaults."""
        config = AgentConfig()
        assert config.max_iterations == 10
        assert config.temperature == 0.7
        assert config.enable_memory is True

    def test_agent_config_temperature_validation(self):
        """Test temperature validation."""
        # Temperature should be between 0 and 2
        config = AgentConfig(temperature=3.5)
        with pytest.raises(ValueError):
            config.validate()

        config = AgentConfig(temperature=-0.1)
        with pytest.raises(ValueError):
            config.validate()

        # Valid temperature
        config = AgentConfig(temperature=1.5)
        config.validate()  # Should not raise

    def test_agent_config_memory_type_validation(self):
        """Test memory type validation."""
        config = AgentConfig(memory_type="invalid")
        with pytest.raises(ValueError):
            config.validate()

        config = AgentConfig(memory_type="in_memory")
        config.validate()  # Should not raise


class TestAppConfig:
    """Tests for AppConfig."""

    def test_app_config_initialization(self):
        """Test app config initialization."""
        config = AppConfig()
        assert config.aws is not None
        assert config.semantic_kernel is not None
        assert config.agent is not None

    def test_app_config_validation(self):
        """Test app config validation."""
        config = AppConfig()
        config.validate()  # Should not raise

    def test_app_config_invalid_environment(self):
        """Test validation with invalid environment."""
        config = AppConfig(env="invalid")
        with pytest.raises(ValueError):
            config.validate()

    def test_app_config_valid_environments(self):
        """Test validation with valid environments."""
        valid_envs = ["development", "testing", "staging", "production"]
        for env in valid_envs:
            config = AppConfig(env=env)
            config.validate()  # Should not raise

    def test_get_config_singleton(self):
        """Test get_config returns singleton."""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_reset_config(self):
        """Test resetting configuration."""
        reset_config()
        config1 = get_config()
        reset_config()
        config2 = get_config()
        assert config1 is not config2
