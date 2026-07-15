"""Unit tests for BaseAgent and specialized agents."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_ai.agents import (
    AgentMessage,
    AgentTask,
    AnalyticsAgent,
    ContentGenerationAgent,
    CustomerServiceAgent,
)


class TestBaseAgent:
    """Tests for BaseAgent functionality."""

    def test_agent_initialization(self, mock_bedrock_client):
        """Test agent initialization."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            
            assert agent.name == "Analytics Agent"
            assert agent.max_iterations == 10
            assert agent.temperature == 0.5

    def test_add_message(self, mock_bedrock_client):
        """Test adding messages to agent."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            agent.add_message("user", "Hello, agent!")
            
            assert len(agent.message_history) == 1
            assert agent.message_history[0].role == "user"
            assert agent.message_history[0].content == "Hello, agent!"

    def test_get_conversation_context(self, mock_bedrock_client):
        """Test getting conversation context."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            agent.add_message("user", "What's 2+2?")
            agent.add_message("assistant", "2+2 = 4")
            agent.add_message("user", "Thanks!")
            
            context = agent.get_conversation_context()
            
            assert len(context) == 3
            assert context[0]["role"] == "user"
            assert context[2]["content"] == "Thanks!"

    def test_get_conversation_context_with_limit(self, mock_bedrock_client):
        """Test getting limited conversation context."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            for i in range(5):
                agent.add_message("user", f"Message {i}")
            
            context = agent.get_conversation_context(max_messages=2)
            
            assert len(context) == 2
            assert "Message 3" in context[0]["content"]

    def test_get_system_prompt(self, mock_bedrock_client):
        """Test system prompt generation."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            prompt = agent.get_system_prompt()
            
            assert "Analytics Agent" in prompt
            assert "Business Intelligence" in prompt

    def test_clear_history(self, mock_bedrock_client):
        """Test clearing message history."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            agent.add_message("user", "Test message")
            assert len(agent.message_history) == 1
            
            agent.clear_history()
            assert len(agent.message_history) == 0

    def test_get_agent_info(self, mock_bedrock_client):
        """Test getting agent information."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            agent.add_message("user", "Test")
            
            info = agent.get_agent_info()
            
            assert info["name"] == "Analytics Agent"
            assert info["messages_count"] == 1


class TestAnalyticsAgent:
    """Tests for AnalyticsAgent."""

    def test_analytics_agent_plan(self, mock_bedrock_client):
        """Test analytics agent planning."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = AnalyticsAgent(MagicMock())
            plan = agent.plan("Analyze sales data", {})
            
            assert isinstance(plan, list)
            assert len(plan) > 0
            assert "analyze" in plan[0].lower()

    def test_analytics_agent_execute_task(self, mock_bedrock_client, mock_bedrock_response):
        """Test analytics agent task execution."""
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = "Analysis complete: Sales increased 15%"
        
        agent = AnalyticsAgent(mock_bedrock)
        
        task = AgentTask(
            task_id="test-001",
            description="Analyze Q3 sales",
            objective="Find trends",
        )
        
        result = agent.execute_task(task)
        
        assert result["status"] == "completed"
        assert result["task_id"] == "test-001"


class TestCustomerServiceAgent:
    """Tests for CustomerServiceAgent."""

    def test_customer_service_agent_plan(self, mock_bedrock_client):
        """Test customer service agent planning."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = CustomerServiceAgent(MagicMock())
            plan = agent.plan("Handle complaint", {})
            
            assert isinstance(plan, list)
            assert "customer" in str(plan).lower() or "inquiry" in str(plan).lower()

    def test_customer_service_agent_execute_task(self, mock_bedrock_client):
        """Test customer service agent task execution."""
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = "We will resolve your issue shortly."
        
        agent = CustomerServiceAgent(mock_bedrock)
        
        task = AgentTask(
            task_id="support-001",
            description="Customer login issue",
            objective="Resolve authentication problem",
        )
        
        result = agent.execute_task(task)
        
        assert result["status"] == "completed"
        assert result["task_id"] == "support-001"


class TestContentGenerationAgent:
    """Tests for ContentGenerationAgent."""

    def test_content_generation_agent_plan(self, mock_bedrock_client):
        """Test content generation agent planning."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = ContentGenerationAgent(MagicMock())
            plan = agent.plan("Write blog post", {})
            
            assert isinstance(plan, list)
            assert "generate" in str(plan).lower() or "write" in str(plan).lower()

    def test_content_generation_temperature(self, mock_bedrock_client):
        """Test that content generation agent has higher temperature."""
        with patch("boto3.client", return_value=mock_bedrock_client):
            agent = ContentGenerationAgent(MagicMock())
            
            # Content generation should have higher temperature than analytics
            assert agent.temperature > 0.7
