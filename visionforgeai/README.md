# VisionForge AI

An AI Workflow Engine capable of generating marketing videos, advertisements, nursery rhymes, educational videos, AI images, storyboards, voiceovers, subtitles, thumbnails, and social media content.

## Overview

VisionForge AI is a production-ready AI Workflow Platform built with modern Python practices. It follows SOLID principles, Clean Architecture, and provides a plugin-based architecture for integrating various AI providers (LLM, image, video, audio, etc.) without tight coupling.

## Features

- **Provider Agnostic**: Easily swap between OpenAI, Anthropic, Ollama, and other AI providers
- **Modular Architecture**: Clean separation of concerns with service, repository, and provider layers
- **Extensible**: Add new workflow types without modifying core system
- **Production Ready**: Comprehensive logging, error handling, validation, and testing
- **Scalable**: Designed for horizontal scaling with support for message queues
- **Secure**: Input validation, output sanitization, and secure secret management
- **Well Tested**: Unit tests for all business logic with >80% coverage target
- **Well Documented**: Auto-generated API docs with Swagger/OpenAPI

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI for high-performance async API
- **Dependency Injection**: Built-in FastAPI dependency system
- **ORM**: SQLAlchemy 2.0 with async support
- **Validation**: Pydantic v2 for data validation and settings management
- **Database**: SQLite (development), PostgreSQL (production)
- **Caching**: Redis (optional)
- **Background Tasks**: Celery
- **Testing**: Pytest with asyncio support
- **Code Quality**: Black, Ruff, MyPy
- **Containerization**: Docker (ready)

## Project Structure

```
VisionForgeAI/
├── api/                 # API route definitions
│   └── routes/          # API endpoint routers
├── config/              # Configuration management
├── docs/                # Documentation
├── models/              # Database and Pydantic models
├── providers/           # AI provider implementations
│   ├── llm/             # Language Model providers
│   ├── image/           # Image generation providers
│   ├── video/           # Video generation providers
│   ├── audio/           # Audio generation providers
│   └── ...              # Other provider types
├── services/            # Business logic services
├── schemas/             # Pydantic schemas for API validation
├── workflows/           # Workflow definitions and orchestration
├── utils/               # Utility functions
├── tests/               # Unit and integration tests
├── templates/           # Jinja2 templates
├── static/              # Static assets
├── prompts/             # AI prompt templates
├── assets/              # Static assets (logos, fonts, etc.)
├── output/              # Generated output storage
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- (Optional) Docker and Docker Compose
- API keys for desired AI providers (OpenAI, Anthropic, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/visionforge-ai.git
   cd visionforge-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. Run database migrations (if using SQLAlchemy with migrations):
   ```bash
   alembic upgrade head
   ```

6. Start the application:
   ```bash
   uvicorn main:app --reload
   ```

7. Visit http://localhost:8000/docs for interactive API documentation

## Usage Examples

### Text Generation

```bash
curl -X POST "http://localhost:8000/api/v1/llm/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

### Streaming Text Generation

```bash
curl -X POST "http://localhost:8000/api/v1/llm/generate/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a short story about a robot learning to paint",
    "temperature": 0.8
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Configuration

All configuration is managed through environment variables or a `.env` file. See `.env.example` for all available options.

Key configuration sections:
- **Application**: Name, version, debug mode, etc.
- **API**: Host, port, workers
- **LLM**: Provider, API keys, model, parameters
- **Database**: Connection URL
- **Storage**: Type (local, S3, GCS, Azure) and credentials
- **External Services**: API keys for image, video, audio providers
- **Feature Flags**: Enable/disable optional functionality

## Development Guidelines

Following the principles established in `prompt.txt`:

1. **Provider Design**: Never couple to one AI provider - each implements a common interface
2. **Extensibility**: Add new workflow types without rewiring the system
3. **Quality First**: Type hints, logging, error handling, validation, tests, documentation
4. **Process**: Design → Implement → Test → Document → Commit
5. **Configuration**: Everything configurable via environment variables or config files
6. **Observability**: Structured logging, metrics, health checks, tracing
7. **Security**: Input validation, output sanitization, secure secrets
8. **Scalability**: Designed for horizontal scaling with message queues
9. **Testability**: Unit tests for all business logic
10. **Documentation**: Docstrings for all public functions/classes, maintained API docs

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=./ --cov-report=html

# Run specific test suite
pytest tests/services/
```

## Docker Deployment

```bash
# Build the image
docker build -t visionforge-ai .

# Run the container
docker run -p 8000:8000 --env-file .env visionforge-ai
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- Inspired by the need for a flexible, provider-agnostic AI workflow platform
- Built with thanks to the open-source AI provider communities
## Project Status

### ✅ Completed
- Provider-agnostic LLM abstraction (base LLMProvider, OpenAI, Anthropic, Mock)
- Factory pattern for dynamic provider selection
- Service layer (LLMService) handling business logic
- FastAPI application setup with lifespan events, middleware, global error handling
- Core API endpoints:
  - `POST /api/v1/llm/generate` (text generation)
  - `POST /api/v1/llm/generate/stream` (streaming via SSE)
  - `GET /api/v1/llm/models` (list available models)
  - `GET /api/v1/llm/health` (provider health check)
  - `GET /` (root info)
  - `GET /health` (application health)
- Dependency injection via `get_settings()` and `get_llm_service()`
- Configuration management using Pydantic Settings with provider‑specific API keys
- Mock LLM provider enabling zero‑cost local testing (returns `[MOCK] <prompt>`)
- Fixed import structure; package can be imported as `visionforgeai`
- Basic directory scaffolding for future providers (image, video, audio) and workflows

### 🚧 In Progress / Pending
- Implement image, video, and audio providers (Stability AI, Replicate, etc.)
- Add authentication & role‑based access control (JWT/OAuth2)
- Implement refresh token flow and user management API
- Add database models and Alembic migrations for persistent storage (users, jobs, results)
- Integrate Celery (or RQ) for long‑running asynchronous jobs (video rendering, etc.)
- Write comprehensive unit & integration tests (target >80% coverage)
- Add OpenAPI/WebSocket support for real‑time job status updates
- Configure CI/CD pipeline (GitHub Actions) with linting, testing, and container builds
- Create Dockerfile and docker‑compose.yml for local development
- Implement request/response logging and structured audit trails
- Add rate limiting and endpoint throttling
- Provide example front‑end (React/Vue) or API consumer documentation

