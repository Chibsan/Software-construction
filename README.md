# Software Construction Project

This repository contains two projects:
1. **SDD Project** - A full-stack nutrition comparison application (Python backend + React frontend)
2. **Vibe Project** - A Python nutrition comparison CLI tool

---

## ⚡ Quick Start (Copy & Paste Ready)

### SDD Project - Terminal 1 (Database)
```bash
cd SDD\ Project && docker-compose up
```

### SDD Project - Terminal 2 (Backend)
```bash
cd SDD\ Project/backend && pip install -e ".[dev]" && alembic upgrade head && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### SDD Project - Terminal 3 (Frontend)
```bash
cd SDD\ Project/frontend && npm install && npm run dev
```

### Vibe Project
```bash
cd Vibe\ project && python nutrition_compare.py
```

---

## Project Structure

```
├── SDD Project/           # Full-stack application (backend + frontend)
│   ├── backend/          # FastAPI server with database
│   ├── frontend/         # React + TypeScript frontend
│   ├── docker-compose.yml
│   └── ...
└── Vibe project/         # Python CLI tool
    ├── nutrition_compare.py
    ├── nutrition_app.html
    └── ...
```

---

## SDD Project

The SDD Project is a full-stack nutrition comparison application with a Python FastAPI backend and React/TypeScript frontend.

### Prerequisites

- **Node.js** (v18+) - for frontend
- **Python** (v3.11+) - for backend
- **Docker & Docker Compose** - for PostgreSQL database
- **PostgreSQL** (or use Docker)

### Backend Setup

The backend is a FastAPI application with SQLAlchemy ORM and Alembic migrations.

#### 1. Install Python Dependencies

```bash
cd SDD\ Project/backend
pip install -e ".[dev]"  # Install package in editable mode with dev dependencies
```

#### 2. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your database and other configuration settings.

#### 3. Start PostgreSQL (via Docker)

From the `SDD Project` root directory:

```bash
docker-compose up -d
```

This starts a PostgreSQL database on `localhost:5432`.

#### 4. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

#### 5. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`.

View API documentation at: `http://localhost:8000/docs`

### Frontend Setup

The frontend is a React + TypeScript application using Vite.

#### 1. Install Dependencies

```bash
cd SDD\ Project/frontend
npm install
```

#### 2. Start the Development Server

```bash
npm run dev
```

The frontend will typically be available at `http://localhost:5173`.

#### 3. Build for Production

```bash
npm run build
```

#### 4. Run Tests

```bash
# Run unit tests
npm test

# Watch mode
npm run test:watch

# E2E tests (Playwright)
npm run test:e2e
```

### Running Both Backend and Frontend

From the `SDD Project` root:

```bash
# Terminal 1: Start database
docker-compose up

# Terminal 2: Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev
```

---

## Vibe Project

The Vibe Project is a Python-based nutrition comparison tool with both CLI and web interface capabilities.

### Prerequisites

- **Python** (v3.11+)

### Setup

#### 1. Install Dependencies (Optional)

If you need to install the package:

```bash
cd Vibe\ project
pip install -e .
```

Or install required packages:

```bash
pip install -r requirements.txt  # if requirements.txt exists
```

#### 2. Run the Main Application

```bash
cd Vibe\ project
python nutrition_compare.py
```

This will start an HTTP server and automatically open `nutrition_app.html` in your browser.

#### 3. Run Tests

```bash
cd Vibe\ project
python -m pytest test_nutrition_compare.py -v
```

### Features

- Compare nutritional values of different food products
- CSV-based data loading from `products.csv`
- Web interface via `nutrition_app.html`
- Ranking by various nutrition metrics (calories, protein, fiber, etc.)

---

## Common Commands

### Backend (SDD Project)

| Command | Purpose |
|---------|---------|
| `pip install -e ".[dev]"` | Install dependencies |
| `alembic upgrade head` | Run database migrations |
| `alembic downgrade -1` | Rollback last migration |
| `uvicorn app.main:app --reload` | Start server with hot reload |
| `pytest` | Run tests |

### Frontend (SDD Project)

| Command | Purpose |
|---------|---------|
| `npm install` | Install dependencies |
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm test` | Run unit tests |
| `npm run test:e2e` | Run e2e tests |

### Docker (SDD Project)

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start services in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs db` | View database logs |

### Vibe Project

| Command | Purpose |
|---------|---------|
| `python nutrition_compare.py` | Run the application |
| `pytest test_nutrition_compare.py -v` | Run tests |

---

## Troubleshooting

### Database Connection Issues (SDD Project)

- Ensure PostgreSQL is running: `docker-compose up -d`
- Check `.env` file has correct database credentials
- Verify port 5432 is not in use: `lsof -i :5432`

### Frontend Can't Connect to Backend

- Ensure backend is running on `http://localhost:8000`
- Check browser console for CORS errors
- Verify `.env` or config has correct backend URL

### Python Version Issues

- Ensure Python 3.11+: `python --version`
- Use virtual environment: `python -m venv .venv && source .venv/bin/activate`

### Port Already in Use

- Backend (8000): `lsof -i :8000`
- Frontend (5173): `lsof -i :5173`
- Database (5432): `lsof -i :5432`

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Vite Documentation](https://vitejs.dev/)

