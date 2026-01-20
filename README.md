# VideoFlix - Video Streaming Platform

A Netflix-like video streaming platform built with Django REST Framework. The application handles video uploads, automatic transcoding to multiple resolutions using HLS (HTTP Live Streaming), and serves content through a RESTful API. It also uses django_rq und redis for background Tasks, and JWT Token for Login through Email verification Link.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Background Processing](#background-processing)
- [Development](#development)
- [Production Deployment](#production-deployment)

## Features

- User authentication with JWT (JSON Web Tokens)
- Email verification for new registrations
- Password reset functionality with email confirmation
- Video upload and management through Django Admin
- Automatic video transcoding to multiple resolutions (480p, 720p, 1080p)
- HLS (HTTP Live Streaming) format for adaptive bitrate streaming
- Automatic thumbnail generation from uploaded videos
- Background task processing for video conversion
- Redis-based caching layer
- RESTful API for video streaming

## Technology Stack

### Backend Framework
- **Django 5.1.4** - Python web framework
- **Django REST Framework 3.16.1** - Toolkit for building Web APIs
- **Gunicorn** - WSGI HTTP Server for production

### Database
- **PostgreSQL** - Primary relational database
- **Redis** - In-memory data structure store for caching and message broker

### Authentication
- **djangorestframework-simplejwt** - JWT authentication
- **HTTP-only cookies** - Secure token storage

### Background Processing
- **Django-RQ** - Asynchronous task queue
- **Redis** - Message broker for task queue

### Video Processing
- **FFMPEG** - Video transcoding and thumbnail generation
- **HLS (HTTP Live Streaming)** - Adaptive bitrate streaming protocol

### Static Files & Media
- **WhiteNoise** - Serves static files efficiently
- **Pillow** - Python Imaging Library for thumbnails

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

### Additional Tools
- **django-cors-headers** - CORS handling for API access

## System Architecture

### Video Processing Pipeline
```
1. Admin uploads video via Django Admin
   ↓
2. Django saves original video and creates database entry (status: pending)
   ↓
3. Django Signal triggers background task
   ↓
4. Redis queue stores the task
   ↓
5. RQ Worker picks up task from queue
   ↓
6. FFMPEG processes video:
   - Creates 480p, 720p, 1080p versions
   - Converts to HLS format (m3u8 + ts segments)
   - Generates thumbnail from video
   ↓
7. Database updated with file paths (status: completed)
   ↓
8. Videos available for streaming via API
```

### Directory Structure
```
VideoFlix/
├── authentication/
│   ├── api/
│   │   ├── serializers.py  # Registration, Login, Password Reset
│   │   ├── views.py        # Authentication endpoints
│   │   └── urls.py         # Authentication URL patterns
│   ├── models.py           # Custom User model, Token models
│   ├── signals.py          # Email verification triggers
│   ├── utils.py            # Email sending utilities
│   └── admin.py            # Admin configuration
├── video_content/
│   ├── api/
│   │   ├── serializers.py  # Video serializers
│   │   ├── views.py        # Video streaming endpoints
│   │   └── urls.py         # Video API URL patterns
│   ├── models.py           # Video model
│   ├── tasks.py            # Background tasks (FFMPEG processing)
│   ├── signals.py          # Video processing triggers
│   └── admin.py            # Admin configuration
├── core/
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── templates/
│   ├── verification_email.html
│   └── password_reset.html
├── media/
│   ├── videos/
│   │   ├── [original videos]
│   │   └── hls/
│   │       └── [video_id]/
│   │           ├── 480p/
│   │           │   ├── index.m3u8
│   │           │   └── segment*.ts
│   │           ├── 720p/
│   │           │   ├── index.m3u8
│   │           │   └── segment*.ts
│   │           └── 1080p/
│   │               ├── index.m3u8
│   │               └── segment*.ts
│   └── thumbnails/
│       └── video_*.jpg
├── static/
├── docker-compose.yml
├── backend.Dockerfile
├── requirements.txt
└── .env
```

## Prerequisites

- Docker Desktop (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Installation


### 1. Clone the repository
```bash
git clone https://github.com/DomCamillo/videoflix.git
cd videoflix
```

### 2. Configure environment variables
Copy the template and fill in your data:
```bash
cp .env.template .env
```

Edit `.env` and set:
- **DJANGO_SUPERUSER_EMAIL**: Your admin email (used for login!)
- **DJANGO_SUPERUSER_USERNAME**: Your admin username
- **DJANGO_SUPERUSER_PASSWORD**: Your admin password
- **EMAIL_HOST_USER**: Your Gmail address
- **EMAIL_HOST_PASSWORD**: Your Gmail App Password


## Email Configuration

For email functionality (registration, password reset), you need to configure Gmail:

1. Enable 2FA in your Google Account
2. Create an App Password: Google Account → Security → 2-Step Verification → App passwords (https://myaccount.google.com/apppasswords)
3. Add to your `.env` file:
```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your_16_digit_app_password
```

### 3. Build and start containers
```bash
docker-compose up --build
```
This will automatically:
-  Run database migrations
-  Create a superuser with your `.env` credentials
-  Start the RQ worker for background tasks
-  Collect static files


**Admin Panel:**
- URL: http://localhost:8000/admin
- *** Login with EMAIL** (not username!): Use `DJANGO_SUPERUSER_EMAIL` from your `.env`
- Password: Use `DJANGO_SUPERUSER_PASSWORD` from your `.env`

---

### Known Issue: Migration Order !!!!

If you encounter a migration dependency error, run migrations in this order:
```bash

docker-compose up -d

docker-compose exec web python manage.py migrate auth
docker-compose exec web python manage.py migrate authentication
docker-compose exec web python manage.py migrate admin
docker-compose exec web python manage.py migrate
```



### 4. Start RQ Worker (in separate terminal)
```bash
docker-compose exec web python manage.py rqworker default
```

## Configuration

### Docker Services

The application consists of three main services:

#### Web (Django Application)
- Runs on port 8000
- Handles API requests
- Serves media files in development

#### Database (PostgreSQL)
- Persistent storage for application data
- Accessed via internal Docker network

#### Redis
- Message broker for Django-RQ
- Cache backend for Django
- Accessed via internal Docker network

### CORS Configuration

Configure allowed origins in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://localhost:8000",
    "http://127.0.0.1:4200",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]
CORS_ALLOW_CREDENTIALS = True
```

### Media Files

Development configuration in `settings.py`:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Add to `urls.py`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## API Endpoints

### Authentication

#### Register
```
POST /api/register/
Body: {
    "email": "user@example.com",
    "password": "SecurePassword123"
}
```

#### Email Activation
```
GET /api/activate/<uidb64>/<token>/
```

#### Login
```
POST /api/login/
Body: {
    "email": "user@example.com",
    "password": "SecurePassword123"
}
```

#### Logout
```
POST /api/logout/
```

#### Token Refresh
```
POST /api/token/refresh/
```

#### Password Reset Request
```
POST /api/password_reset/
Body: {
    "email": "user@example.com"
}
```

#### Password Reset Confirm
```
POST /api/password_confirm/<uidb64>/<token>/
Body: {
    "new_password": "NewSecurePassword123",
    "confirm_password": "NewSecurePassword123"
}
```

### Video Streaming

#### Get Video List
```
GET /api/video/
Response: [
    {
        "id": 1,
        "created_at": "2023-01-01T12:00:00Z",
        "title": "Movie Title",
        "description": "Movie Description",
        "thumbnail_url": "http://localhost:8000/media/thumbnails/video_1.jpg",
        "category": "Drama"
    }
]
```

#### Get HLS Playlist
```
GET /api/video/<movie_id>/<resolution>/index.m3u8
Example: GET /api/video/1/720p/index.m3u8
```

#### Get Video Segment
```
GET /api/video/<movie_id>/<resolution>/<segment>/
Example: GET /api/video/1/720p/segment000.ts
```

## Background Processing

### Video Processing Task

When a video is uploaded, the following background task is triggered:

1. **Thumbnail Generation**
   - Extracts frame at 3 seconds
   - Scales to 1280x720
   - Saves as JPEG

2. **Video Transcoding**
   - Converts to three resolutions: 480p, 720p, 1080p
   - Creates HLS format (m3u8 playlist + ts segments)
   - 10-second segments for optimal streaming

3. **Database Update**
   - Updates video status to 'completed'
   - Stores paths to HLS directories

### Task Monitoring

View RQ worker logs:
```bash
docker-compose logs -f web
```

Check Redis queue:
```bash
docker-compose exec redis redis-cli
> KEYS *
```

## Development

### Running Tests
```bash
docker-compose exec web python manage.py test
```

### Accessing Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Database Operations
```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Database shell
docker-compose exec db psql -U videoflix_user -d videoflix_db
```

### Collect Static Files
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

## Production Deployment

### Environment Variables

Set `DEBUG=False` and configure production settings:
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=production_secret_key
```

### Media Files

For production, use a dedicated file server or cloud storage:

**For Example: Nginx**
```nginx
location /media/ {
    alias /app/media/;
}
```

### Database

Use a managed PostgreSQL service or configure production database settings.

### Gunicorn Configuration

The application uses Gunicorn with the following configuration:
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Security Checklist

- Set strong `SECRET_KEY`
- Enable HTTPS
- Configure `SECURE_SSL_REDIRECT = True`
- Set `SESSION_COOKIE_SECURE = True`
- Set `CSRF_COOKIE_SECURE = True`
- Configure `ALLOWED_HOSTS` properly
- Use environment variables for sensitive data
- Enable database connection pooling
- Configure proper CORS origins

## Troubleshooting

### Video not processing

Check RQ worker is running:
```bash
docker-compose exec web python manage.py rqworker default
```

### FFMPEG errors

Verify FFMPEG is installed:
```bash
docker-compose exec web ffmpeg -version
```

### Database connection issues

Check PostgreSQL is running:
```bash
docker-compose ps
```

### Redis connection issues

Test Redis connection:
```bash
docker-compose exec redis redis-cli ping
```

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact: dominic@moerth.ch