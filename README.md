# 🤖 Resume AI Generator

A powerful AI-driven platform for resume generation, optimization, and job matching with dual-mode functionality, Google Gemini AI integration, and professional document downloads.

## ✨ Features

- 🆕 **Generate New Resume**: Create resumes from job descriptions
- 🔧 **Optimize Existing Resume**: Enhance your current resume for specific jobs  
- 📋 **Interview Questions**: Generate behavioral, technical, and company-specific questions
- 📄 **Multiple Formats**: Download resumes in PDF and DOCX formats
- 🔐 **Secure Authentication**: JWT-based user authentication
- 🎨 **Modern UI**: Responsive design with Tailwind CSS
- 🚀 **Fast Performance**: Docker containerized with Redis caching

## 📁 Project Structure

For detailed project organization, see [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 🚀 Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd resume-ai-generator
   cp .env.example .env
   ```

2. **Configure AI services** in `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Optional
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - 🌐 **Frontend**: http://localhost:3000
   - 🔧 **Backend API**: http://localhost:8000
   - 📚 **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│   (Next.js)     │────│   (FastAPI)     │────│  Google Gemini  │
│   Port: 3000    │    │   Port: 8000    │    │    OpenAI       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │              ┌─────────────────┐              
         │              │   PostgreSQL    │              
         └──────────────│   Port: 5433    │              
                        └─────────────────┘              
                                 │                       
                        ┌─────────────────┐              
                        │     Redis       │              
                        │   Port: 6379    │              
                        └─────────────────┘              
```

## Entity Relationship Diagram

```
+---------------+       +---------------+       +---------------+
|     User      |       |  TokenUsage   |       |UserBudgetSettings|
+---------------+       +---------------+       +---------------+
| id            |<----->| id            |       | id            |
| email         |       | user_id       |<----->| user_id       |
| hashed_password|       | endpoint_type  |       | daily_limit    |
| is_active     |       | tokens_used    |       | monthly_limit  |
| is_admin      |       | cost           |       | created_at     |
| created_at    |       | created_at     |       | updated_at     |
+---------------+       +---------------+       +---------------+
        |                      ^
        |                      |
        v                      |
+---------------+       +---------------+
|     Job       |       |    Resume     |
+---------------+       +---------------+
| id            |       | id            |
| user_id       |       | user_id       |
| title         |       | job_id        |<------+
| company       |       | content       |       |
| description   |<------| ai_enhanced   |       |
| created_at    |       | created_at    |       |
+---------------+       +---------------+       |
                               |                |
                               +----------------+
```

## Features

- AI-powered resume generation based on job descriptions
- ATS validation and optimization
- Cover letter generation
- Interview question preparation
- Token usage tracking and budget management
- Rate limiting for API endpoints
- Admin dashboard for usage statistics

## Project Structure

```
resume-ai-generator/
├── frontend/           # Next.js frontend
│   ├── components/     # React components
│   ├── pages/          # Next.js pages
│   ├── services/       # API services
│   └── styles/         # CSS styles
├── backend/            # FastAPI backend
│   ├── app/            # Application code
│   │   ├── auth/       # Authentication
│   │   ├── db/         # Database models
│   │   ├── middleware/ # Middleware (rate limiting)
│   │   ├── routers/    # API routes
│   │   └── services/   # Business logic
│   ├── tests/          # Test suite
│   └── alembic/        # Database migrations
└── docker-compose.yml  # Docker compose configuration
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Node.js 16+ (for local development)
- Python 3.9+ (for local development)
- AI provider API key

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-ai-generator.git
   cd resume-ai-generator
   ```

2. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   docker-compose up
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# On Windows
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_ai
set SECRET_KEY=your_secret_key
set OPENAI_API_KEY=your_openai_api_key
set REDIS_URL=redis://localhost:6379/0

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

## Sharing and Deployment

- Copy `.env.example` to `.env` for local development, or use `.env.multi-ai-example` if you want the expanded multi-provider settings.
- Keep real API keys and production secrets out of GitHub. The repository `.gitignore` already excludes `.env`, `.env.local`, and `.env.production`.
- Docker Compose is the fastest way to boot the full stack locally; for backend-only development, the API can also run with SQLite and a placeholder OpenAI key if you are only testing startup.

## API Reference

### Authentication

- `POST /auth/register`: Register a new user
- `POST /auth/login`: Login and get access token
- `GET /auth/me`: Get current user information

### Resumes

- `POST /resumes/`: Create a new resume
- `GET /resumes/{resume_id}`: Get a resume by ID
- `POST /resumes/generate`: Generate an AI-enhanced resume

### Jobs

- `POST /jobs/analyze`: Analyze a job description
- `POST /jobs/match`: Match a resume to a job description

### Generate

- `POST /generate/cover-letter`: Generate a cover letter
- `POST /generate/interview-questions`: Generate interview questions

### Validate

- `POST /validate/ats`: Validate a resume against ATS systems

### Admin

- `GET /admin/token-usage`: Get overall token usage statistics
- `GET /admin/token-usage/users/{user_id}`: Get user-specific token usage
- `GET /admin/token-usage/endpoints`: Get endpoint-specific token usage
- `GET /admin/token-usage/daily`: Get daily token usage statistics

### Budget

- `GET /budget/settings`: Get user budget settings
- `POST /budget/settings`: Create or update budget settings
- `DELETE /budget/settings`: Reset budget settings

## Demo Flow (3-minute click-through)

1. **Registration and Login**
   - Register a new account
   - Login with your credentials

2. **Upload Resume or Create New**
   - Upload an existing resume
   - Or create a new one from scratch

3. **Job Search and Analysis**
   - Enter a job description or paste a job posting URL
   - View the extracted key skills and requirements

4. **Resume Enhancement**
   - Generate an AI-enhanced resume tailored to the job
   - Review and edit the generated content

5. **ATS Validation**
   - Check your resume against ATS systems
   - Get recommendations for improvements

6. **Cover Letter Generation**
   - Generate a matching cover letter
   - Customize and download

7. **Interview Preparation**
   - Generate potential interview questions
   - Practice with AI-generated answers

8. **Budget Management**
   - Set daily and monthly token usage limits
   - Monitor your usage in the dashboard

## Sample Data

The application comes with sample data for testing:

- Sample resumes in various formats
- Sample job descriptions from different industries
- Pre-configured user accounts:
  - Regular user: `user@example.com` / `password`
  - Admin user: `admin@example.com` / `password`

## Monitoring and Metrics

The application includes Prometheus and Grafana for monitoring:

- Access Grafana: http://localhost:3001 (admin/admin)
- Access Prometheus: http://localhost:9090

## Deployment

The application can be deployed to AWS ECS/Fargate or Railway/Vercel using the included GitHub Actions workflow.

## License

MIT