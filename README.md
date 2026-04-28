# CodingSchool

An online learning management system (LMS) built with Django. Students purchase subscription plans to access programming courses, complete video lessons with quizzes and homework, and receive feedback from teachers.

## Features

- **Authentication** — email-based registration with email verification, login, password reset, and profile management (avatar, country, GitHub/LinkedIn links)
- **Subscription plans** — three tiers (Newbie, Middle, Pro) with flexible durations (1 month, 3 months, 6 months, 1 year, or lifetime)
- **Promo codes** — admin-generated codes that activate a subscription plan for a student
- **Courses & lessons** — video lessons (YouTube embed), PDF notes, and JSON-based lesson content; lessons unlock sequentially as the student progresses
- **Lesson tests** — multiple-choice quizzes with a configurable minimum passing score
- **Homework submissions** — students submit a GitHub link; teachers review and mark as approved, pending, or needs revision
- **Comments & reports** — students can comment on lessons and report issues
- **Admin/teacher dashboard** — overview of pending homework, student progress, and submitted reports
- **Email notifications** — confirmation emails, password reset emails, and homework submission alerts

## Tech Stack

- **Python 3 / Django 5.1**
- **PostgreSQL** — primary database
- **Redis** — caching backend and django-select2 cache
- **Django REST Framework** — API layer
- **django-select2** — searchable dropdowns for country and status fields
- **Pillow** — user avatar uploads
- **python-dotenv** — environment variable management

## Project Structure

```
codingschool/
├── config/          # Django project settings and root URL configuration
├── users/           # Custom user model, subscription plans, promo codes, country data
├── course/          # Courses, lessons, tests, homework, comments, reports
├── main/            # Public pages (index, courses overview, dashboard, promo code page)
└── manage.py
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd codingschool
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Fill in `.env` with your database credentials, secret key, and email settings.

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Load country data**

   ```bash
   python manage.py load_countries
   ```

7. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

8. **Start Redis** (required for caching)

   ```bash
   redis-server
   ```

9. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   The app will be available at `http://127.0.0.1:8000`.

### Initial Data Setup

After running the server, log in to the Django admin (`/admin/`) and create:

- Programming languages and bonus modules (used in subscription plans)
- Subscription plan modes and duration types
- At least one `Course` with `Lesson` objects
- A teacher group named `teachers` to grant dashboard access to non-superuser staff

## Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `POSTGRES_ENGINE` | DB engine (`django.db.backends.postgresql`) |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `EMAIL_BACKEND` | Email backend class |
| `EMAIL_HOST` | SMTP host (e.g. `smtp.gmail.com`) |
| `EMAIL_HOST_USER` | Sender email address |
| `EMAIL_HOST_PASSWORD` | SMTP password or app password |

## License

This project is for portfolio and educational purposes.
