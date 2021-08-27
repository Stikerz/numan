"""
WSGI config for numan_python_takehome project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""
import os

import dotenv
from django.core.wsgi import get_wsgi_application

dotenv.load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "numan_python_takehome.settings")

application = get_wsgi_application()
