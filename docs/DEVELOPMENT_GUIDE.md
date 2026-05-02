# 🛠️ Development Guide

## Project Organization

The Resume AI Generator project is now properly organized with a clean structure:

### 📂 Directory Structure

```
resume-ai-generator/
├── 📄 README.md                 # Main documentation
├── 📄 docker-compose.yml        # Development environment
├── 📄 .gitignore               # Git ignore rules
├── 📄 .env                     # Environment variables
├── 📂 backend/                 # FastAPI backend
├── 📂 frontend/                # Next.js frontend  
├── 📂 docker/                  # Docker configurations
├── 📂 tests/                   # All test files
├── 📂 scripts/                 # Utility scripts
└── 📂 docs/                    # Documentation
```

## 🚀 Development Workflow

### 1. **Environment Setup**
```bash
# Copy environment template
cp .env.multi-ai-example .env

# Edit .env with your API keys
nano .env
```

### 2. **Start Development Environment**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. **Testing**
```bash
# Run API tests
python tests/api/test_*.py

# Run integration tests
python tests/integration/test_*.py

# Run frontend tests
python tests/frontend/test_*.py
```

### 4. **Debugging**
```bash
# Use utility scripts
python scripts/debug_project.py
python scripts/list_gemini_models.py
```

## 📝 Code Organization

### Backend (`/backend`)
- **`app/main.py`**: FastAPI application entry
- **`app/routers/`**: API route handlers
- **`app/services/`**: Business logic
- **`app/models/`**: Database models
- **`app/auth/`**: Authentication logic

### Frontend (`/frontend`)
- **`pages/dashboard.tsx`**: Main resume interface
- **`components/`**: Reusable UI components
- **`services/`**: API integration
- **`types/`**: TypeScript definitions

### Tests (`/tests`)
- **`api/`**: Backend API tests
- **`frontend/`**: Frontend component tests
- **`integration/`**: End-to-end tests

## 🔧 Development Tips

### Adding New Features
1. **Backend**: Add routes in `backend/app/routers/`
2. **Frontend**: Add components in `frontend/components/`
3. **Tests**: Add tests in appropriate `/tests` subdirectory
4. **Documentation**: Update relevant docs in `/docs`

### File Naming Conventions
- **Backend**: `snake_case` for Python files
- **Frontend**: `PascalCase` for React components
- **Tests**: `test_*.py` prefix for test files
- **Scripts**: Descriptive names in `scripts/`

### Environment Management
- **Development**: Use `docker-compose.yml`
- **Production**: Use `docker/docker-compose.prod.yml`
- **Infrastructure**: Use `docker/docker-compose.infrastructure.yml`

### API Development
1. **Add route** in `backend/app/routers/`
2. **Add service** in `backend/app/services/`
3. **Add test** in `tests/api/`
4. **Update frontend** service calls

### UI Development
1. **Create component** in `frontend/components/`
2. **Add to page** in `frontend/pages/`
3. **Style with Tailwind** CSS classes
4. **Add TypeScript** types in `types/`

## 🐛 Debugging

### Backend Issues
```bash
# View backend logs
docker-compose logs backend

# Enter backend container
docker-compose exec backend bash

# Run backend tests
docker-compose exec backend pytest
```

### Frontend Issues
```bash
# View frontend logs
docker-compose logs frontend

# Enter frontend container
docker-compose exec frontend bash

# Rebuild frontend
docker-compose build frontend
```

### Database Issues
```bash
# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d resumedb
```

## 🚀 Deployment

### Production Build
```bash
# Build production images
docker-compose -f docker/docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Environment Variables
Ensure all production environment variables are set:
- `GEMINI_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`

## 📚 Resources

- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**: Detailed project structure
- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)**: Integration guide
- **[MULTI_AI_SETUP.md](MULTI_AI_SETUP.md)**: AI service setup
- **Backend API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000