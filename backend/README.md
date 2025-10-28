# 🏗️ Oover Backend

Django REST Framework backend for the Oover sport prediction application.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Database Management](#database-management)
- [Testing](#testing)
- [Project Structure](#project-structure)

## ✨ Features

- 🔐 RESTful API with Django REST Framework
- 🗄️ PostgreSQL database (Supabase)
- 📚 Auto-generated API documentation (OpenAPI/Swagger)
- 🔄 CORS support for Next.js frontend
- 🚀 Async task support with Celery (optional)
- 🧪 Comprehensive test suite
- 📊 Data models for countries, leagues, teams, matches, and predictions

## 🛠️ Tech Stack

- **Framework**: Django 5.0.1
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (via Supabase)
- **Documentation**: drf-spectacular
- **Task Queue**: Celery (optional)
- **Server**: Gunicorn (production), Django dev server (development)

## 📦 Prerequisites

- Python 3.10+
- PostgreSQL (Supabase account)
- pip or pipenv
- Virtual environment (recommended)

## 🚀 Installation

### 1. Clone the repository

```bash
cd backend
```

### 2. Create a virtual environment

```bash
# Using venv
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Or using conda
conda create -n oover python=3.10
conda activate oover
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Create .env file

```bash
cp .env.example .env
```

### 2. Fill in your environment variables

Edit `.env` and add your Supabase credentials:

```env
# Required
DB_PASSWORD=your-supabase-password
DB_HOST=db.rmyxqqcozxbapyldeicm.supabase.co

# Optional
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
```

**⚠️ Important**: Get your Supabase password from:
Supabase Dashboard → Project Settings → Database → Password

### 3. Generate a Django secret key (production)

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## 🏃 Running the Server

### Development Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

### Production Server

```bash
# Using Gunicorn
gunicorn oover_backend.wsgi:application --bind 0.0.0.0:8000

# Or using Uvicorn (with async support)
uvicorn oover_backend.asgi:application --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/api/docs/swagger/
- **ReDoc**: http://localhost:8000/api/docs/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/docs/schema/

## 🗄️ Database Management

### Connect to existing Supabase tables

The backend connects to tables already created by Prisma migrations. No need to run Django migrations for existing tables.

### Verify database connection

```bash
python manage.py dbshell
```

### Create Django migrations (for new models)

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Create a superuser (admin)

```bash
python manage.py createsuperuser
```

Access admin panel at: http://localhost:8000/admin/

## 🧪 Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=apps --cov-report=html
```

### Run specific tests

```bash
pytest apps/core/tests/test_serializers.py
```

## 📁 Project Structure

```
backend/
├── oover_backend/          # Django project configuration
│   ├── __init__.py
│   ├── settings.py        # Main settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI config
│   ├── asgi.py            # ASGI config
│   └── celery.py          # Celery config
│
├── apps/                   # Django apps
│   └── core/              # Core app (countries, etc.)
│       ├── models.py      # Database models
│       ├── serializers/   # DRF serializers
│       ├── views/         # API views
│       ├── urls.py        # App URLs
│       └── tests/         # Tests
│
├── manage.py              # Django CLI
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔌 API Endpoints

### Countries

- `GET /api/countries/` - List all countries
- `GET /api/countries/{id}/` - Get country details
- `POST /api/countries/` - Create country
- `PUT /api/countries/{id}/` - Update country
- `DELETE /api/countries/{id}/` - Delete country

### More endpoints coming soon...

- Leagues
- Teams
- Matches
- Predictions

## 🛠️ Development Commands

### Format code

```bash
black .
isort .
```

### Lint code

```bash
flake8
mypy .
```

### Database shell

```bash
python manage.py dbshell
```

### Django shell

```bash
python manage.py shell
```

## 🐛 Troubleshooting

### Database connection error

- Check your Supabase password in `.env`
- Ensure your IP is whitelisted in Supabase (Settings → Database → Network)
- Verify database host is correct

### Import errors

- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### CORS errors

- Check `CORS_ALLOWED_ORIGINS` in `settings.py`
- Ensure Next.js is running on the correct port (3000)

## 📝 Notes

- This backend connects to existing Supabase tables created by Prisma
- Database models are defined but set to `managed=False` to avoid conflicts
- Environment variables are loaded from `.env` file using `python-dotenv`
- All API responses follow RESTful conventions

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Format code with black and isort
5. Submit pull request

## 📄 License

Private project - All rights reserved

---

**Author**: Oover Development Team  
**Date**: October 2025  
**Version**: 1.0.0
