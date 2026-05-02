# 📁 Project Structure

## Overview
This document outlines the organized structure of the Resume AI Generator project.

```
resume-ai-generator/
├── 📄 README.md                   # Main project documentation
├── 📄 docker-compose.yml          # Main Docker Compose configuration
├── 📄 .env                        # Environment variables
├── 📄 .env.production             # Production environment variables
├── 📄 .env.multi-ai-example       # Multi-AI configuration example
│
├── 📂 backend/                     # FastAPI Backend Application
│   ├── 📄 Dockerfile              # Backend Docker configuration
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📄 alembic.ini             # Database migration configuration
│   ├── 📂 app/                    # Main application code
│   │   ├── 📄 main.py             # FastAPI application entry point
│   │   ├── 📄 database.py         # Database configuration
│   │   ├── 📂 api/                # API route modules
│   │   ├── 📂 auth/               # Authentication logic
│   │   ├── 📂 core/               # Core application logic
│   │   ├── 📂 models/             # Database models
│   │   ├── 📂 routers/            # API routers
│   │   ├── 📂 services/           # Business logic services
│   │   └── 📂 workers/            # Background task workers
│   ├── 📂 alembic/                # Database migrations
│   ├── 📂 tests/                  # Backend unit tests
│   └── 📂 uploads/                # File upload storage
│
├── 📂 frontend/                    # Next.js Frontend Application
│   ├── 📄 Dockerfile              # Frontend Docker configuration
│   ├── 📄 package.json            # Node.js dependencies
│   ├── 📄 next.config.js          # Next.js configuration
│   ├── 📄 tailwind.config.js      # Tailwind CSS configuration
│   ├── 📄 tsconfig.json           # TypeScript configuration
│   ├── 📂 components/             # React components
│   ├── 📂 pages/                  # Next.js pages
│   ├── 📂 public/                 # Static assets
│   ├── 📂 services/               # API service calls
│   ├── 📂 styles/                 # CSS and styling
│   └── 📂 types/                  # TypeScript type definitions
│
├── 📂 docker/                      # Docker Configuration Files
│   ├── 📄 docker-compose.backend.yml      # Backend-specific services
│   ├── 📄 docker-compose.infrastructure.yml # Infrastructure services
│   ├── 📄 docker-compose.monitoring.yml    # Monitoring services
│   └── 📄 docker-compose.prod.yml          # Production configuration
│
├── 📂 tests/                       # Project-wide Tests
│   ├── 📂 api/                    # API integration tests
│   ├── 📂 frontend/               # Frontend tests
│   ├── 📂 integration/            # End-to-end integration tests
│   └── 📄 *.py                    # Various test files
│
├── 📂 scripts/                     # Utility Scripts
│   ├── 📄 list_gemini_models.py   # Script to list available AI models
│   └── 📄 *.py                    # Other utility and debug scripts
│
├── 📂 docs/                        # Documentation
│   ├── 📄 PROJECT_STRUCTURE.md    # This file - project structure
│   ├── 📄 INTEGRATION_COMPLETE.md # Integration completion guide
│   ├── 📄 MULTI_AI_SETUP.md       # Multi-AI setup documentation
│   └── 📄 context.txt             # Project context information
│
└── 📂 .github/                     # GitHub Configuration
    └── 📂 workflows/               # GitHub Actions workflows
```

## Key Directories

### 🚀 **Backend (`/backend`)**
- **FastAPI-based REST API** serving resume generation and optimization
- **PostgreSQL database** integration with SQLAlchemy ORM
- **AI services** integration (Google Gemini, OpenAI)
- **Authentication** and authorization with JWT
- **File upload/processing** capabilities
- **Background tasks** with Celery and Redis

### 🎨 **Frontend (`/frontend`)**
- **Next.js React application** with TypeScript
- **Tailwind CSS** for styling
- **Dual-mode interface** for resume generation/optimization
- **Interview questions** generation feature
- **Document download** functionality (PDF/DOCX)
- **Responsive design** for mobile and desktop

### 🐳 **Docker (`/docker`)**
- **Modular Docker Compose** configurations
- **Environment-specific** setups (dev, prod, monitoring)
- **Service orchestration** for microservices architecture

### 🧪 **Tests (`/tests`)**
- **API tests** for backend endpoints
- **Frontend tests** for UI components
- **Integration tests** for end-to-end workflows
- **Organized by test type** for better maintainability

### 📝 **Documentation (`/docs`)**
- **Technical documentation** and setup guides
- **API documentation** and integration notes
- **Deployment guides** and configuration examples

## Development Workflow

1. **Local Development**: Use `docker-compose.yml` for local development
2. **Testing**: Run tests from `/tests` directory
3. **Production**: Use configurations in `/docker` for production deployment
4. **Documentation**: Update `/docs` when adding new features

## Getting Started

1. **Clone the repository**
2. **Copy environment files**: `.env.multi-ai-example` to `.env`
3. **Start services**: `docker-compose up -d`
4. **Access application**: 
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Services Architecture

- **Frontend**: Next.js app (Port 3000)
- **Backend**: FastAPI app (Port 8000)  
- **Database**: PostgreSQL (Port 5433)
- **Cache**: Redis (Port 6379)
- **Monitoring**: Grafana, Prometheus (when enabled)