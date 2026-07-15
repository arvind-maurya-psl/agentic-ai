"""Unit tests for agent coordinator."""

from unittest.mock import MagicMock

import pytest

from agentic_ai.agents import (
    AgentCoordinator,
    AgentTask,
    AnalyticsAgent,
    CustomerServiceAgent,
)


class TestAgentCoordinator:
    """Tests for AgentCoordinator."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator with mock agents."""
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = "Mock response"
        
        agents = {
            "analytics": AnalyticsAgent(mock_bedrock),
            "support": CustomerServiceAgent(mock_bedrock),
        }
        return AgentCoordinator(agents)

    def test_coordinator_initialization(self, coordinator):
        """Test coordinator initialization."""
        assert len(coordinator.agents) == 2
        assert "analytics" in coordinator.agents
        assert "support" in coordinator.agents

    def test_delegate_task_success(self, coordinator):
        """Test successful task delegation."""
        task = AgentTask(
            task_id="test-001",
            description="Test task",
            objective="Test objective",
        )

        result = coordinator.delegate_task(task, "analytics")

        assert result["status"] == "completed"
        assert result["task_id"] == "test-001"

    def test_delegate_task_invalid_agent(self, coordinator):
        """Test task delegation with invalid agent."""
        task = AgentTask(
            task_id="test-001",
            description="Test task",
            objective="Test objective",
        )

        result = coordinator.delegate_task(task, "nonexistent")

        assert result["status"] == "failed"
        assert "not found" in result["error"]

    def test_route_task_analytics(self, coordinator):
        """Test auto-routing to analytics agent."""
        task = AgentTask(
            task_id="test-001",
            description="Analyze sales data trends",
            objective="Identify patterns",
        )

        result = coordinator.route_task(task)

        # Should route to analytics based on keywords
        assert result["status"] == "completed"

    def test_route_task_support(self, coordinator):
        """Test auto-routing to support agent."""
        task = AgentTask(
            task_id="test-001",
            description="Customer has login issue",
            objective="Resolve support ticket",
        )

        result = coordinator.route_task(task)

        # Should route to support based on keywords
        assert result["status"] == "completed"

    def test_execute_workflow(self, coordinator):
        """Test workflow execution."""
        tasks_data = [
            {"description": "Analyze data", "objective": "Get insights"},
            {"description": "Customer support", "objective": "Resolve issue"},
        ]

        # Convert to AgentTask objects
        tasks = [
            AgentTask(
                task_id=f"task-{i}",
                description=task_data["description"],
                objective=task_data["objective"],
            )
            for i, task_data in enumerate(tasks_data)
        ]

        result = coordinator.execute_workflow("Test workflow", tasks)

        assert result["objective"] == "Test workflow"
        assert result["task_count"] == 2

    def test_get_agent_stats(self, coordinator):
        """Test getting agent statistics."""
        stats = coordinator.get_agent_stats()

        assert "analytics" in stats
        assert "support" in stats
        assert "name" in stats["analytics"]

    def test_execution_history(self, coordinator):
        """Test execution history tracking."""
        # Execute some tasks
        task = AgentTask(
            task_id="test-001",
            description="Test",
            objective="Test",
        )
        coordinator.delegate_task(task, "analytics")

        history = coordinator.get_execution_history()

        assert len(history) > 0
        assert history[0]["task_id"] == "test-001"
