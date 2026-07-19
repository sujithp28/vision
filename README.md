# VisionForge AI

An AI-powered educational video planning platform designed for content creators, with a focus on independence from third-party APIs and affordability for educational content creation.

## Overview

VisionForge AI is an AI Workflow Platform specifically built for educational video planning. It enables content creators to generate detailed video plans for educational content using local LLMs, eliminating dependency on expensive third-party APIs. The platform follows SOLID principles, Clean Architecture, and provides a plugin-based architecture for integrating various AI providers with a focus on local LLM independence for affordability and privacy.

## Key Features

- **Provider Agnostic**: Easily switch between OpenAI, Anthropic, Ollama, and local LLM providers (including llama.cpp)
- **Local LLM Support**: Integrated Phi-3-mini model via llama.cpp for zero-cost, private inference
- **Educational Focus**: Specialized prompt templating system for educational video content
- **Modular Architecture**: Clean separation of concerns with service, repository, and provider layers
- **Extensible**: Add new workflow types without modifying core system
- **Production Ready**: Comprehensive logging, error handling, validation, and testing
- **Scalable**: Designed for horizontal scaling with support for message queues
- **Secure**: Input validation, output sanitization, and secure secret management
- **Well Tested**: Unit tests for all business logic with >80% coverage target
- **Educational Video Planner**: End-to-end system for generating video plans for educational content

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

4. Download the Phi-3-mini model:
   ```bash
   mkdir -p models
   # Download the model from Hugging Face or similar source
   # Example: wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct.q4_k_m.gguf -O models/phi-3-mini-4k-instruct.q4_k_m.gguf
   ```

5. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   # Important: Set LLM_PROVIDER=local and LOCAL_MODEL_PATH=./models/phi-3-mini-4k-instruct.q4_k_m.gguf
   ```

6. Start the application:
   ```bash
   uvicorn main:app --reload
   ```

7. Visit http://localhost:8000/docs for interactive API documentation
8. Visit http://localhost:8000 for the web interface

## Usage Examples

### Educational Video Planning

```bash
curl -X POST "http://localhost:8000/api/v1/video/planner/" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain photosynthesis to kids",
    "target_audience": "children aged 8-10 years",
    "video_length": 5,
    "educational_goal": "Understand how plants make food from sunlight",
    "include_activities": true,
    "include_assessment": true
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Visit http://localhost:8000/docs for interactive API documentation

## Configuration

All configuration is managed through environment variables or a `.env` file. See `.env.example` for all available options.

Key configuration sections:
- **Application**: Name, version, debug mode, etc.
- **API**: Host, port, workers
- **LLM**: Provider, API keys, model, parameters
- **LOCAL_MODEL_PATH**: Path to the local LLM model file (used when LLM_PROVIDER is 'local')
- **Database**: Connection URL
- **Storage**: Type (local, S3, GCS, Azure) and credentials
- **External Services**: API keys for image, video, audio providers
- **Feature Flags**: Enable/disable optional functionality

## Development Guidelines

Following the principles established in our development process:

1. **Provider Design**: Never couple to one AI provider - each implements a common interface
2. **Local LLM Priority**: Primary focus on local LLM independence for affordability and privacy
3. **Educational Focus**: Specialized prompts and templates for educational content creation
4. **Extensibility**: Add new workflow types without rewiring the system
5. **Quality First**: Type hints, logging, error handling, validation, tests, documentation
6. **Process**: Design → Implement → Test → Document → Commit
7. **Configuration**: Everything configurable via environment variables or config files
8. **Observability**: Structured logging, metrics, health checks, tracing
9. **Security**: Input validation, output sanitization, secure secrets
10. **Scalability**: Designed for horizontal scaling with message queues
11. **Testability**: Unit tests for all business logic
12. **Documentation**: Docstrings for all public functions/classes, maintained API docs

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

## Project Status

### ✅ Completed

- **Local LLM Implementation**: Integrated Phi-3-mini model via llama.cpp for zero-cost inference
- **Provider-Agnostic LLM Abstraction**: Base LLMProvider with local, OpenAI, Anthropic, and Mock implementations
- **Dynamic Provider Selection**: Factory pattern for runtime provider selection
- **Service Layer**: LLMService handling business logic and provider management
- **FastAPI Application**: Proper setup with lifespan events, middleware, and global error handling
- **Core API Endpoints**:
  - `POST /api/v1/llm/generate` (text generation)
  - `POST /api/v1/llm/generate/stream` (streaming via SSE)
  - `GET /api/v1/llm/models` (list available models)
  - `GET /api/v1/llm/health` (provider health check)
  - `GET /` (root info)
  - `GET /health` (application health)
- **Educational Video Planner**: 
  - `POST /api/v1/video/planner/` endpoint for generating video plans
  - Intelligent prompt templating system (educational_kids, educational_general, general)
  - VideoPlannerRequest and VideoPlannerResponse Pydantic models
- **Frontend Implementation**: 
  - Responsive HTML/JS interface at `/public/index.html`
  - Form for video planning parameters with client-side validation
  - Integration with backend API using Fetch API
  - Markdown rendering of generated video plans using marked.js
- **Dependency Injection**: Via `get_settings()` and `get_llm_service()`
- **Configuration Management**: Pydantic Settings with environment variable support
- **Static File Serving**: Configured to serve frontend from `/public` directory
- **CORS Configuration**: Properly configured for frontend-backend communication
- **Logging**: Structured logging with structlog and python-json-logger
- **Error Handling**: Custom exception hierarchy with standardized JSON responses
- **Import Structure**: Fixed imports; package can be imported as `visionforgeai`
- **Directory Structure**: Complete scaffolding for providers, services, API routes, etc.

### 🚧 In Progress / Pending

- **User Testing**: Conduct actual testing with educators and content creators
- **User Authentication**: Implement authentication & role‑based access control (JWT/OAuth2)
- **Persistence Layer**: Add database models and Alembic migrations for storage (users, projects, video plans)
- **Asynchronous Processing**: Integrate Celery (or RQ) for long‑running jobs
- **Video Generation Pipeline**: Extend beyond planning to actual video generation
- **Additional Templates**: More prompt templates for different content types (marketing, entertainment, etc.)
- **Performance Optimization**: 
  - GPU acceleration options
  - Model quantization experiments
  - Batching capabilities for concurrent users
- **Deployment Preparation**:
  - Dockerfile and docker‑compose.yml for local development
  - CI/CD pipeline (GitHub Actions) with linting, testing, and container builds
- **Monitoring & Analytics**:
  - Request/response logging and structured audit trails
  - Usage tracking and analytics
  - Rate limiting and endpoint throttling
- **Testing**:
  - Comprehensive unit & integration tests (target >80% coverage)
  - End-to-end testing of the video planning workflow
- **Documentation**:
  - API consumer documentation
  - Deployment guides
  - User guides for educators and content creators

## Educational Focus Validation

The system has been specifically tested and validated for educational use cases:

1. **Photosynthesis Explanation** (8-10 years):
   - Generated comprehensive video plans including:
     - Hook/Introduction suggestions for grabbing children's attention
     - Main content segments with clear explanations
     - Visual suggestions (animations, demonstrations, etc.)
     - Engagement techniques (questions, calls-to-action)
     - Summary and call-to-action
     - Suggested hands-on activities and experiments
     - Assessment ideas to check understanding

2. **Water Cycle Explanation** (6-9 years):
   - Similar comprehensive educational video planning output tailored for younger children

## Affordability Achievement

By eliminating reliance on paid API services and utilizing open-source local LLMs:

- **Zero Ongoing API Costs**: After initial model download, no recurring API fees
- **Hardware Requirements**: Runs on standard CPU (no GPU required for basic operation)
- **Scalability**: Can serve multiple users from a single instance
- **Privacy**: All processing happens locally, ensuring data privacy and compliance
- **Accessibility**: Makes educational video planning accessible to educators, homeschooling parents, and content creators on limited budgets

## Next Steps

1. **User Testing**: Conduct actual testing with educators and content creators to gather feedback
2. **Feature Enhancement**:
   - Implement user authentication and project saving
   - Add more specialized prompt templates for different educational subjects and age groups
   - Extend to actual video generation capabilities (beyond planning)
3. **Performance Optimization**:
   - Explore GPU acceleration options for improved performance
   - Implement caching mechanisms for improved response times
   - Experiment with different model quantization levels
4. **Production Readiness**:
   - Containerize with Docker for easy deployment
   - Set up monitoring, logging, and alerting
   - Implement backup and disaster recovery procedures
   - Establish CI/CD pipeline for automated testing and deployment

## Educational Impact

VisionForge AI addresses the core problem of expensive educational video creation tools by providing:

1. **Cost Elimination**: No ongoing API costs after initial setup
2. **Technological Independence**: No reliance on third-party AI providers that may change pricing or terms
3. **Educational Specialization**: Prompts and templates specifically designed for educational content
4. **Accessibility**: Enables educators with limited budgets to create professional-quality video plans
5. **Privacy & Security**: All content processing happens locally, protecting sensitive educational material
6. **Scalability**: Can be deployed internally by educational institutions or used individually by creators

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need for affordable, independent AI tools for educational content creation
- Built with thanks to the open-source AI provider communities (particularly the llama.cpp and Phi-3 model teams)
- Created to empower educators and content creators to produce high-quality educational content without financial barriers