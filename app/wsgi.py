"""WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from app.utils.config import setup_django_environment

setup_django_environment(from_command_line=True)

application = get_wsgi_application()
