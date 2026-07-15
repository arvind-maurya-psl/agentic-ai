"""Integration tests for the complete Agentic AI system."""

from unittest.mock import MagicMock, patch

import pytest

from agentic_ai.app import AgenticAIApplication


class TestAgenticAIApplication:
    """Integration tests for AgenticAIApplication."""

    @pytest.fixture
    def app(self):
        """Create an application instance."""
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = "Mock AI response"

        with patch("agentic_ai.kernel_factory.BedrockService") as MockService:
            mock_service = MagicMock()
            mock_service.invoke_model.return_value = "Mock response"
            MockService.return_value = mock_service

            app = AgenticAIApplication()
            app.bedrock_service = mock_bedrock

            # Update agents with mock bedrock
            for agent in app.agents.values():
                agent.bedrock_service = mock_bedrock

            return app

    def test_app_initialization(self, app):
        """Test application initialization."""
        assert app.config is not None
        assert len(app.agents) == 3
        assert app.coordinator is not None

    def test_execute_task_with_agent(self, app):
        """Test executing a task with specific agent."""
        result = app.execute_task(
            description="Analyze data",
            objective="Get insights",
            agent_name="analytics",
        )

        assert result["status"] == "completed"

    def test_execute_task_auto_routed(self, app):
        """Test executing auto-routed task."""
        result = app.execute_task(
            description="Analyze sales trends",
            objective="Identify patterns",
        )

        assert result["status"] == "completed"

    def test_execute_workflow(self, app):
        """Test workflow execution."""
        tasks_data = [
            {
                "description": "Analyze quarterly data",
                "objective": "Identify trends",
            },
            {
                "description": "Write market analysis",
                "objective": "Create report",
            },
        ]

        result = app.execute_workflow("Market Analysis", tasks_data)

        assert result["objective"] == "Market Analysis"
        assert result["task_count"] == 2

    def test_collaborate_agents(self, app):
        """Test agent collaboration."""
        result = app.collaborate_agents(
            primary_agent="content_generation",
            secondary_agents=["analytics"],
            description="Create data-driven report",
            objective="Combine analysis and writing",
        )

        assert "primary_result" in result
        assert "secondary_consultations" in result

    def test_get_system_info(self, app):
        """Test getting system information."""
        info = app.get_system_info()

        assert "bedrock_model" in info
        assert "agents" in info
        assert "config" in info


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_workflow(self):
        """Test a complete workflow from task to result."""
        mock_bedrock = MagicMock()
        mock_bedrock.invoke_model.return_value = "Workflow completed successfully"

        with patch("agentic_ai.kernel_factory.BedrockService") as MockService:
            mock_service = MagicMock()
            mock_service.invoke_model.return_value = "Report generated"
            mock_service.get_model_info.return_value = {"model_id": "claude"}
            MockService.return_value = mock_service

            app = AgenticAIApplication()
            app.bedrock_service = mock_bedrock

            for agent in app.agents.values():
                agent.bedrock_service = mock_bedrock

            # Execute workflow
            workflow_result = app.execute_workflow(
                objective="Complete business analysis",
                tasks_data=[
                    {
                        "description": "Analyze financial data",
                        "objective": "Extract key metrics",
                    },
                    {
                        "description": "Prepare presentation",
                        "objective": "Create executive summary",
                    },
                ],
            )

            # Validate workflow
            assert workflow_result["task_count"] == 2
            assert workflow_result["completed_count"] >= 0
