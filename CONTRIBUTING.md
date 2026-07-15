# Contributing to Agentic AI

We welcome contributions from the community! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Assume good intentions
- Focus on what is best for the community
- Show empathy towards other contributors

## Getting Started

1. **Fork the repository**
2. **Create a feature branch** from `develop`
3. **Make your changes**
4. **Submit a pull request**

## Development Setup

Follow the [Development Guide](DEVELOPMENT.md) for detailed setup instructions.

## Making Changes

### Before You Start

1. Check issue tracker for similar work
2. Comment on the issue to discuss your approach
3. Fork the repository
4. Create a feature branch: `git checkout -b feature/your-feature`

### Code Style

We follow PEP 8 with these tools:
- **Black**: Code formatting (line length: 100)
- **Ruff**: Linting
- **isort**: Import sorting
- **mypy**: Type checking

Run before committing:
```bash
black src/ tests/
ruff check --fix src/ tests/
isort src/ tests/
mypy src/
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build, dependencies, CI changes

Examples:
```
feat(agents): add new analytics agent

fix(bedrock): resolve timeout on large responses

docs(readme): add deployment examples

test(coordinator): increase test coverage
```

### Writing Tests

- Write tests before code (TDD preferred)
- Aim for >80% code coverage
- Use descriptive test names
- Mock external dependencies (AWS Bedrock, etc.)

Example:
```python
def test_agent_execution_success(self):
    """Test successful agent task execution."""
    agent = AnalyticsAgent(MagicMock())
    task = AgentTask(task_id="1", description="Test", objective="Test")
    
    result = agent.execute_task(task)
    
    assert result["status"] == "completed"
    assert result["task_id"] == "1"
```

### Documentation

- Update docstrings for all public functions/classes
- Update README if adding features
- Include examples for new functionality
- Keep CHANGELOG.md updated

## Pull Request Process

1. **Ensure your changes pass all checks**
   ```bash
   ruff check src/ tests/
   black --check src/ tests/
   isort --check-only src/ tests/
   pytest tests/ --cov=src/agentic_ai
   ```

2. **Update documentation**
   - Docstrings in code
   - README.md (if user-facing)
   - DEVELOPMENT.md (if developer-facing)

3. **Submit PR to `develop` branch**
   - Clear description of changes
   - Link related issues
   - Add screenshots/examples if applicable

4. **Address review feedback**
   - Respond to comments
   - Make requested changes
   - Re-request review when ready

5. **Merge when approved**
   - Squash commits if requested
   - Delete feature branch
   - Update issue status

## Areas for Contribution

### Code
- New agents or plugins
- Better error handling
- Performance optimization
- Security improvements

### Documentation
- README improvements
- Docstring enhancements
- Tutorial/guide creation
- Example code

### Testing
- Unit test coverage
- Integration tests
- Performance tests
- Edge case testing

### Infrastructure
- GitHub Actions improvements
- Docker optimization
- Deployment scripts
- Configuration examples

## Reporting Issues

### Bug Reports

Include:
- Python and OS version
- Reproducible steps
- Expected vs actual behavior
- Relevant logs/errors

Example:
```
**Describe the bug**
Agent execution times out when processing large datasets.

**To Reproduce**
1. Create analytics agent
2. Execute task with 10000+ records
3. Agent fails after 5 minutes

**Expected behavior**
Agent should handle large datasets or provide helpful error message.

**Environment**
- Python 3.12
- AWS Region: us-east-1
- Bedrock Model: claude-3-5-sonnet
```

### Feature Requests

Include:
- Clear use case
- Expected behavior
- Possible implementation approach
- Examples if applicable

Example:
```
**Is your feature request related to a problem?**
Users need to store conversation history for audit purposes.

**Describe the solution**
Add database backend for conversation storage with retention policies.

**Alternatives considered**
- Redis persistence (lacks audit trail)
- CSV export (manual and error-prone)

**Additional context**
Many enterprise customers require audit compliance.
```

## Review Process

### For Reviewers

- Provide constructive feedback
- Request changes clearly
- Approve when satisfied
- Be respectful and helpful

### For Contributors

- Respond promptly to feedback
- Ask for clarification if needed
- Make changes as requested
- Thank reviewers

## Performance Considerations

When contributing, consider:
- Algorithm complexity (aim for O(n) or better)
- Memory usage (avoid loading entire datasets)
- API call optimization (batch where possible)
- Cache strategies
- Concurrency and parallelization

## Security

### Security Best Practices

- Never hardcode credentials
- Validate all inputs
- Use environment variables for secrets
- Keep dependencies updated
- Follow OWASP guidelines

### Reporting Security Vulnerabilities

**Do not open public issues for security vulnerabilities.**

Email: security@example.com with:
- Vulnerability description
- Affected versions
- Proof of concept (if safe)
- Suggested fix (if you have one)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CHANGELOG.md
- GitHub contributors page
- Release notes (for significant contributions)

## Questions?

- Check existing issues and discussions
- Review documentation
- Ask in pull request comments
- Open a discussion issue

## Additional Resources

- [Development Guide](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
- [GitHub Issues](https://github.com/org/agentic-ai/issues)
- [Discussions](https://github.com/org/agentic-ai/discussions)

Thank you for contributing to Agentic AI! 🚀
