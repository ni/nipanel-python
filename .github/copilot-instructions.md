# Copilot Instructions for nipanel-python

## Repository Overview

**nipanel** is a Python package that provides support for creating and controlling measurement and visualization panels. It's developed by NI and enables Python applications to create Streamlit-based panels that can be served and controlled via gRPC services.

### Key Repository Information
- **Language**: Python (3.10+)
- **Package Manager**: Poetry 2.1+
- **Framework**: Uses Streamlit for panel UI, gRPC for communication
- **Size**: Medium-sized repository (~1300 lines of code in src/)
- **Architecture**: Client-server model with Python panel service and Streamlit frontend
- **Testing**: Comprehensive test suite with unit, integration, and acceptance tests

## Build and Validation Commands

**CRITICAL**: Always run commands in this exact order for successful builds and validation.

### Environment Setup
```powershell
# 1. Verify Poetry is installed (required version 2.1+)
poetry --version

# 2. Install project dependencies (ALWAYS run first)
poetry install

# 3. For examples and development work
poetry install --with examples

# 4. For documentation work
poetry install --with docs
```

### Development Workflow Commands
Follow this sequence when making changes:

```powershell
# 1. Run linting (shows warnings but continues)
poetry run nps lint

# 2. Apply automatic formatting fixes
poetry run nps fix

# 3. Run static type checking (must pass)
poetry run mypy

# 4. Run security analysis (must pass)
poetry run bandit -c pyproject.toml -r src/nipanel

# 5. Run all tests (must pass)
poetry run pytest -v

# 6. Run only unit tests (faster feedback)
poetry run pytest ./tests/unit -v

# 7. Run tests with coverage
poetry run pytest ./tests/unit -v --cov=nipanel
```

### Documentation Build
```powershell
# Build documentation (may fail due to external SSL cert issues - this is expected)
poetry run sphinx-build docs docs/_build --builder html --fail-on-warning
```

### Runtime Requirements
- **Python**: 3.10+
- **Poetry**: 2.1+ required for build system
- **Virtual Environment**: Configured in-project (`.venv/` directory)

## Project Layout and Architecture

### Source Code Structure
```
src/nipanel/                 # Main package directory
├── __init__.py             # Public API exports
├── _streamlit_panel.py     # Core StreamlitPanel class
├── _panel_client.py        # gRPC client for panel communication
├── _panel_value_accessor.py # Value management for panels
├── _streamlit_panel_initializer.py # Panel creation utilities
├── _convert.py             # Type conversion utilities
├── controls/               # Streamlit UI control components
├── converters/             # Type conversion modules
├── panel_refresh/          # Panel refresh functionality
└── streamlit_refresh/      # Streamlit-specific refresh logic
```

### Configuration Files
- **pyproject.toml**: Main project configuration, dependencies, tool settings
- **poetry.toml**: Poetry configuration (sets `in-project = true` for venv)
- **.github/workflows/**: Complete CI/CD pipeline

### Test Structure
```
tests/
├── unit/                   # Unit tests (primary test suite)
├── integration/            # Integration tests
├── acceptance/             # End-to-end acceptance tests
├── utils/                  # Test utilities and fakes
└── conftest.py            # Pytest configuration and fixtures
```

### Examples
```
examples/
├── hello/                  # Basic panel example
├── all_types/              # Demonstrates all supported data types
├── simple_graph/           # Graph visualization example
├── nidaqmx/               # Hardware integration examples
└── performance_checker/    # Performance monitoring example
```

## CI/CD Pipeline

The repository uses a comprehensive GitHub Actions pipeline:

1. **check_nipanel.yml**: Runs on Windows, Ubuntu, macOS with Python 3.10, 3.14
   - Linting with `poetry run nps lint`
   - Type checking with `poetry run mypy`
   - Security scanning with `poetry run bandit -c pyproject.toml -r src/nipanel`

2. **run_unit_tests.yml**: Cross-platform testing (Windows, Ubuntu) with Python 3.10-3.14
   - Unit tests: `poetry run pytest ./tests/unit -v --cov=nipanel --junitxml=test_results/nipanel-{os}-py{version}.xml`

3. **check_docs.yml**: Documentation validation
   - Lock file verification: `poetry check --lock`
   - Documentation build: `poetry run sphinx-build docs docs/_build -b html -W`

### Key Dependencies
- **Core Runtime**: grpcio, protobuf, streamlit, nitypes, numpy, debugpy
- **NI Packages**: ni-grpc-extensions, ni-measurementlink-discovery-v1-client, ni-protobuf-types, ni-panels-v1-proto
- **Development Tools**: ni-python-styleguide, mypy, bandit, pytest

## Architecture Overview

**nipanel** implements a client-server architecture:

1. **Python Application**: Uses nipanel API to create and control panels
2. **Panel Service**: Separate gRPC service (PythonPanelService - external dependency)
3. **Streamlit Frontend**: Web-based UI for the panels
4. **Communication**: gRPC for Python ↔ Service, HTTP for Service ↔ Streamlit

### Core Classes
- `StreamlitPanel`: Main panel interface
- `PanelValueAccessor`: Manages panel state and values
- `create_streamlit_panel()`: Factory function for panel creation

## Validation Steps

### Pre-commit Validation (replicate CI locally)
```powershell
# Complete validation sequence
poetry install
poetry run nps lint
poetry run nps fix
poetry run mypy
poetry run bandit -c pyproject.toml -r src/nipanel
poetry run pytest -v
```

### Common Issues and Solutions

1. **Poetry Lock Issues**: Run `poetry check --lock` to verify lock file consistency
2. **Import Warnings**: flake8_import_order pkg_resources warnings are expected and harmless
3. **Documentation SSL Errors**: External inventory fetch failures are known issues

### File System Requirements
- Virtual environment created in `.venv/` (configured in poetry.toml)
- Test results written to `test_results/` directory
- Documentation built to `docs/_build/`

## Trust These Instructions

These instructions are comprehensive and tested. Only perform additional searches if:
- Commands fail unexpectedly
- You need to understand specific implementation details not covered here
- You're working with files not mentioned in this overview

The build and test commands listed here are the authoritative source - they match exactly what the CI pipeline runs and have been validated to work correctly.