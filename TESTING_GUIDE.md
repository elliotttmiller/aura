# Testing Guide for Aura Sentient Interactive Studio

## Overview

This document provides comprehensive guidance for testing the Aura application, covering both frontend (TypeScript/React) and backend (Python/FastAPI) components.

## Test Infrastructure

### Frontend Testing Stack

- **Framework**: Vitest
- **Testing Library**: @testing-library/react
- **DOM Matchers**: @testing-library/jest-dom
- **Coverage**: @vitest/coverage-v8
- **Environment**: jsdom

### Backend Testing Stack

- **Framework**: Pytest
- **Async Testing**: pytest-asyncio
- **HTTP Client**: httpx (for FastAPI testing)
- **Coverage**: pytest-cov

## Running Tests

### Frontend Tests

```bash
cd frontend/static

# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test src/store/designStore.test.ts
```

### Backend Tests

```bash
# Run all tests
python3 -m pytest

# Run with verbose output
python3 -m pytest -v

# Run specific test file
python3 -m pytest tests/test_security.py

# Run specific test class
python3 -m pytest tests/test_security.py::TestSecurityConfig

# Run specific test method
python3 -m pytest tests/test_security.py::TestSecurityConfig::test_generate_api_key

# Run with coverage
python3 -m pytest --cov=backend --cov-report=html

# Run only unit tests
python3 -m pytest -m unit

# Run excluding slow tests
python3 -m pytest -m "not slow"
```

## Test Organization

### Frontend Test Structure

```
frontend/static/src/
├── components/
│   └── __tests__/          # Component tests
│       └── MyComponent.test.tsx
├── store/
│   └── designStore.test.ts  # Store tests
└── test/
    └── setup.ts             # Test setup and configuration
```

### Backend Test Structure

```
tests/
├── test_security.py         # Security module tests
├── test_exceptions.py       # Exception handling tests
├── test_api_endpoints.py    # API endpoint tests (to be created)
└── test_integration.py      # Integration tests (to be created)
```

## Writing Tests

### Frontend Test Example

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  beforeEach(() => {
    // Setup before each test
  })

  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('should handle click events', () => {
    render(<MyComponent />)
    const button = screen.getByRole('button')
    fireEvent.click(button)
    // Assert expected behavior
  })
})
```

### Backend Test Example

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestMyEndpoint:
    def test_success_case(self):
        response = client.post("/api/endpoint", json={"data": "value"})
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_error_case(self):
        response = client.post("/api/endpoint", json={})
        assert response.status_code == 400
```

## Test Markers (Backend)

Use pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, external dependencies)
- `@pytest.mark.slow` - Slow tests (> 1 second)
- `@pytest.mark.requires_ai` - Tests requiring AI services
- `@pytest.mark.requires_blender` - Tests requiring Blender

Example:
```python
@pytest.mark.unit
def test_fast_function():
    assert my_function() == expected_result

@pytest.mark.integration
@pytest.mark.requires_ai
async def test_ai_integration():
    result = await call_ai_service()
    assert result is not None
```

## Coverage Goals

### Current Coverage Status

- Frontend: Not yet measured (infrastructure in place)
- Backend: Not yet measured (infrastructure in place)

### Target Coverage

- **Overall**: 70% minimum
- **Critical Paths**: 90%+ (security, authentication, core business logic)
- **UI Components**: 60%+ (focus on business logic, not styling)

## Continuous Integration

Tests run automatically on every push and pull request via GitHub Actions:

```yaml
# .github/workflows/ci.yml
- Frontend tests run on Node.js 20
- Backend tests run on Python 3.8, 3.9, 3.10, 3.11, 3.12
- Coverage reports uploaded to Codecov
```

## Test Best Practices

### General

1. **Arrange-Act-Assert**: Structure tests in three clear sections
2. **One assertion per test**: Focus tests on single behaviors
3. **Descriptive names**: Test names should describe what they test
4. **Independent tests**: Tests should not depend on each other
5. **Fast tests**: Keep unit tests fast (< 100ms)

### Frontend Specific

1. **Test user behavior**: Focus on what users see and do
2. **Avoid implementation details**: Don't test internal state directly
3. **Use semantic queries**: Prefer `getByRole`, `getByLabelText` over `getByTestId`
4. **Mock external dependencies**: Mock API calls, avoid real network requests
5. **Cleanup**: Always cleanup after tests (handled automatically by setup)

### Backend Specific

1. **Use test client**: Test FastAPI endpoints with TestClient
2. **Mock external services**: Mock AI services, Blender execution
3. **Test error cases**: Ensure error handling works correctly
4. **Database isolation**: Use separate test database or in-memory storage
5. **Async testing**: Use `pytest.mark.asyncio` for async functions

## Mocking Guidelines

### Frontend Mocks

```typescript
// Mock API calls
vi.mock('./api', () => ({
  fetchData: vi.fn().mockResolvedValue({ data: 'mocked' })
}))

// Mock WebGL canvas
HTMLCanvasElement.prototype.getContext = vi.fn()

// Mock store
vi.mock('./store', () => ({
  useDesignStore: vi.fn(() => ({
    session: { objects: [] }
  }))
}))
```

### Backend Mocks

```python
# Mock AI service
@pytest.fixture
def mock_ai_service(monkeypatch):
    async def mock_generate(*args, **kwargs):
        return {"result": "mocked"}
    
    monkeypatch.setattr("backend.ai_orchestrator.generate", mock_generate)

# Mock Blender execution
@pytest.fixture
def mock_blender(monkeypatch):
    def mock_run_blender(*args, **kwargs):
        return {"success": True}
    
    monkeypatch.setattr("backend.blender_visualizer.run_blender", mock_run_blender)
```

## Debugging Tests

### Frontend

```bash
# Run tests in UI mode for debugging
npm run test:ui

# Add debugger statements in tests
it('should work', () => {
  debugger  // Will pause execution
  expect(true).toBe(true)
})

# Check console output
npm run test -- --reporter=verbose
```

### Backend

```bash
# Run with extra verbosity
python3 -m pytest -vv

# Show print statements
python3 -m pytest -s

# Drop into debugger on failure
python3 -m pytest --pdb

# Stop on first failure
python3 -m pytest -x
```

## Known Issues & Limitations

### Current Limitations

1. **Root __init__.py**: Contains Blender-specific code that prevents normal import
   - **Workaround**: Tests use direct module imports without going through root package

2. **setup.py**: Contains Blender-specific code
   - **Impact**: Cannot test Blender integration without Blender environment
   - **Solution**: Mock Blender-specific functions in tests

3. **AI Services**: Tests should mock AI services to avoid:
   - Rate limiting
   - API costs
   - Network dependencies
   - Slow tests

## Future Improvements

- [ ] Add E2E tests with Playwright
- [ ] Add visual regression testing
- [ ] Implement mutation testing
- [ ] Add performance benchmarks
- [ ] Create test fixtures for common scenarios
- [ ] Add contract tests for API
- [ ] Implement load testing
- [ ] Add security testing (OWASP checks)

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Last Updated**: October 17, 2025
**Version**: 1.0.0
