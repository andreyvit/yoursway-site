#!/usr/bin/env python
import os

from werkzeug import run_simple, DebuggedApplication
from django.views import debug
from django.core.handlers.wsgi import WSGIHandler

def null_technical_500_response(request, exc_type, exc_value, tb):
    raise exc_type, exc_value, tb
debug.technical_500_response = null_technical_500_response

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

if __name__ == '__main__':
    run_simple('0.0.0.0', 8080, DebuggedApplication(WSGIHandler(), True), True)
