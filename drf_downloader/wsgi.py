"""
WSGI config for drf_downloader project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import requests
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_downloader.settings')

application = get_wsgi_application()

# Автозагрузка при старте WSGI
try:
    if settings.AUTOLOAD_ENABLED:
        url = 'http://elasticsearch:9200/file_index'
        data = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text"
                    }
                }
            }
        }
        response = requests.put(url, json=data)
except Exception as e:
    print(e)
