# Chemical Equipment Backend (Django)

## Setup (local)
1. Create virtualenv and install:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. Run dev server:
   ```
   python manage.py runserver
   ```

## Deployment on Render
- Ensure `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS`, `DEBUG` are set in Render environment settings.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn project.wsgi:application`
