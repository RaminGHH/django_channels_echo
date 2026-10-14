# Django Channels Echo

## Setup

```bash
django-admin startproject channel_lab
cd channel_lab
python manage.py startapp echo
python -m venv venv_channel_lab
source venv_channel_lab/bin/activate   # Windows: venv_channel_lab\Scripts\activate
pip install -r requirements.txt


# settings.py
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "echo.apps.ChatConfig",
]

ASGI_APPLICATION = "config.asgi.application"

# run django server
python manage.py runserver

# In other command line
python -m websockets ws://127.0.0.1:8000/ws/echo/

# input (write)
> {"message": "hello"}

# output 
< {"echo": "HELLO"}
```