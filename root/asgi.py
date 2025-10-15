# root/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

# Standard ASGI application for Django HTTP requests
application = get_asgi_application()
