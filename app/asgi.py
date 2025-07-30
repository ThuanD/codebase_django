"""ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

from app.utils.config import setup_django_environment

setup_django_environment(from_command_line=True)

application = get_asgi_application()
