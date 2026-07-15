# Development Guide

This guide explains the codebase structure and development workflows.

## Development Environment Setup

### Initial Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/org/agentic-ai.git
   cd agentic-ai
   ```

2. **Create virtual environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   pip install -e ".[dev,api]"
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   export AWS_REGION=us-east-1
   export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

5. **Verify setup**
   ```bash
   python -c "from agentic_ai.config import get_config; print(get_config())"
   ```

## Project Architecture

### Module Organization

```
src/agentic_ai/
├── agents/              # Multi-agent orchestration
│   ├── base_agent.py    # Abstract base class for all agents
│   ├── specialized_agents.py  # Concrete agent implementations
│   ├── coordinator.py   # Multi-agent orchestrator
│   └── memory_manager.py # Conversation memory management
├── plugins/             # AI function plugins
│   ├── calculator.py    # Mathematical operations
│   ├── web_search.py    # Search and web operations
│   └── data_analysis.py # Data processing tools
├── services/            # External integrations
│   └── bedrock_service.py # AWS Bedrock LLM client
├── utils/               # Utility functions
│   └── logging_util.py  # Logging, formatting, exceptions
├── config.py           # Configuration management
├── kernel_factory.py   # Semantic Kernel configuration
└── app.py             # Main application entry point
```

### Key Components

#### 1. BaseAgent
Abstract base class for all agents. Implements:
- Message history management
- System prompt generation
- Conversation context
- Task execution interface

#### 2. Specialized Agents
Concrete implementations:
- **AnalyticsAgent**: Data analysis, lower temperature (0.5)
- **CustomerServiceAgent**: Support, balanced temperature (0.7)
- **ContentGenerationAgent**: Writing, higher temperature (0.8)

#### 3. AgentCoordinator
- Routes tasks to appropriate agents
- Coordinates multi-agent workflows
- Manages execution history
- Supports agent collaboration

#### 4. BedrockService
- Wraps AWS Bedrock API
- Supports streaming and non-streaming
- Error handling and retries
- Model info retrieval

## Development Workflow

### Adding a New Agent

1. **Create agent class**
   ```python
   # src/agentic_ai/agents/specialized_agents.py
   
   class NewAgent(BaseAgent):
       def __init__(self, bedrock_service, enable_memory=True):
           super().__init__(
               name="New Agent",
               role="Specific role",
               description="Description",
               bedrock_service=bedrock_service,
               temperature=0.6,
           )
       
       def plan(self, objective, context):
           return ["Step 1", "Step 2", "Step 3"]
       
       def execute_task(self, task):
           # Implementation
           pass
   ```

2. **Register in coordinator**
   ```python
   # src/agentic_ai/app.py
   self.agents = {
       "new_agent": NewAgent(self.bedrock_service),
   }
   ```

3. **Add tests**
   ```python
   # tests/unit/test_agents.py
   class TestNewAgent:
       def test_new_agent_init(self):
           agent = NewAgent(MagicMock())
           assert agent.name == "New Agent"
   ```

4. **Update documentation**

### Adding a New Plugin

1. **Create plugin file**
   ```python
   # src/agentic_ai/plugins/new_plugin.py
   
   class NewPlugin:
       @staticmethod
       def new_function(param1, param2):
           """Function description."""
           result = do_something(param1, param2)
           return result
   ```

2. **Add tests**
   ```python
   # tests/unit/test_plugins.py
   def test_new_plugin():
       result = NewPlugin.new_function(1, 2)
       assert result == expected
   ```

3. **Export from plugin module**
   ```python
   # src/agentic_ai/plugins/__init__.py
   from .new_plugin import NewPlugin
   ```

### Modifying Configuration

Configuration uses Pydantic dataclasses:

```python
# src/agentic_ai/config.py
@dataclass
class NewConfig:
    option1: str = os.getenv("OPTION1", "default")
    option2: int = int(os.getenv("OPTION2", "10"))
    
    def validate(self) -> None:
        if not self.option1:
            raise ValueError("OPTION1 required")
```

Then add to `AppConfig`:
```python
@dataclass
class AppConfig:
    new_config: NewConfig = None
    
    def __post_init__(self):
        if self.new_config is None:
            self.new_config = NewConfig()
```

## Testing

### Test Structure

```
tests/
├── conftest.py            # Shared fixtures
├── unit/                  # Unit tests
│   ├── test_agents.py
│   ├── test_bedrock_service.py
│   ├── test_coordinator.py
│   ├── test_config.py
│   └── test_plugins.py
└── integration/           # Integration tests
    └── test_app_integration.py
```

### Writing Tests

1. **Unit Test Example**
   ```python
   def test_agent_add_message(self):
       agent = AnalyticsAgent(MagicMock())
       agent.add_message("user", "Hello")
       
       assert len(agent.message_history) == 1
       assert agent.message_history[0].content == "Hello"
   ```

2. **Mocking Bedrock**
   ```python
   @pytest.fixture
   def mock_bedrock():
       return MagicMock()
   
   def test_with_mock(mock_bedrock):
       mock_bedrock.invoke_model.return_value = "Response"
       # Test code
   ```

3. **Integration Test Example**
   ```python
   def test_complete_workflow(app):
       result = app.execute_task(
           description="Test",
           objective="Test objective"
       )
       assert result["status"] == "completed"
   ```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/agentic_ai --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v

# Run with markers
pytest -m "not slow" tests/

# Watch mode (requires pytest-watch)
ptw tests/
```

## Code Quality

### Linting

```bash
# Run Ruff linter
ruff check src/ tests/

# Fix automatically
ruff check --fix src/

# Run all checks
ruff check src/ && black --check src/ && isort --check-only src/
```

### Formatting

```bash
# Black formatting
black src/ tests/

# Import sorting
isort src/ tests/

# Type checking
mypy src/
```

### Pre-commit Hooks

1. **Install pre-commit**
   ```bash
   pip install pre-commit
   ```

2. **Create .pre-commit-config.yaml** (if not exists)
   ```yaml
   repos:
     - repo: local
       hooks:
         - id: black
           name: black
           entry: black
           language: system
           types: [python]
         - id: ruff
           name: ruff
           entry: ruff check --fix
           language: system
           types: [python]
   ```

3. **Install hooks**
   ```bash
   pre-commit install
   ```

## Common Development Tasks

### Debug Logging

```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug message: {variable}")
logger.info(f"Info message")
logger.warning(f"Warning message")
logger.error(f"Error message")
```

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python -m agentic_ai.app
```

### Testing with Real Bedrock

To test against real AWS Bedrock (requires AWS credentials):

1. **Set environment variables**
   ```bash
   export AWS_REGION=us-east-1
   export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
   ```

2. **Run integration tests**
   ```bash
   pytest tests/integration/ -v -s
   ```

3. **Monitor costs**
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2024-01-01,End=2024-01-02 \
     --granularity DAILY \
     --metrics BlendedCost
   ```

### Debugging in VS Code

1. **Create .vscode/launch.json**
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Current File",
               "type": "python",
               "request": "launch",
               "program": "${file}",
               "console": "integratedTerminal"
           },
           {
               "name": "Python: Pytest",
               "type": "python",
               "request": "launch",
               "module": "pytest",
               "args": ["${file}", "-v"],
               "console": "integratedTerminal"
           }
       ]
   }
   ```

2. **Set breakpoints and run**

### Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = app.execute_task("Test", "Test")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

## Git Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Hotfix: `hotfix/description`
- Release: `release/v1.0.0`

### Commit Messages

Follow conventional commits:

```
feat: add new agent type
fix: resolve task execution timeout
tests: add unit tests for coordinator
docs: update README with examples
chore: update dependencies
```

### Pull Request Process

1. Create feature branch from `develop`
2. Make changes and commit
3. Push branch and open PR
4. Address review comments
5. Ensure CI/CD passes
6. Squash and merge to `develop`

## Documentation

### Code Documentation

```python
def execute_task(self, task: AgentTask) -> dict:
    """
    Execute a task with this agent.
    
    Args:
        task: Task to execute
    
    Returns:
        Result dictionary with status and output
    
    Raises:
        TaskExecutionError: If task execution fails
    """
    pass
```

### Update Documentation

1. Update docstrings in code
2. Update README sections
3. Add examples if adding features
4. Update API documentation

## Troubleshooting Development

### Issue: Import errors
```
Solution: Ensure virtual environment is activated and dependencies installed
pip install -e ".[dev]"
```

### Issue: Tests failing with mocks
```
Solution: Check that mock return values match expected interface
Use mock_bedrock.invoke_model.return_value = "response"
```

### Issue: Bedrock API errors in local testing
```
Solution: Use mock Bedrock service, or ensure AWS credentials configured
export AWS_PROFILE=your-profile
```

## Best Practices

1. **Type hints**: Use type hints for all function signatures
2. **Error handling**: Always handle exceptions gracefully
3. **Logging**: Use structured logging for debugging
4. **Testing**: Write tests before code (TDD)
5. **Documentation**: Keep docstrings up to date
6. **Code review**: Request reviews before merging
7. **Performance**: Profile before optimizing
8. **Security**: Never commit credentials or secrets

## Useful Commands

```bash
# Install development mode
pip install -e ".[dev,api]"

# Run tests with output
pytest -s tests/

# Run tests in parallel
pytest -n auto tests/

# Check code complexity
radon cc src/ -a -nb

# Generate dependency tree
pipdeptree

# Update dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Create distribution
python -m build

# Test package locally
pip install dist/agentic_ai-*.whl
```

## References

- [Semantic Kernel Docs](https://learn.microsoft.com/en-us/semantic-kernel/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Pytest Docs](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
