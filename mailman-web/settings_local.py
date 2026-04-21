import os

DEBUG = False

LANGUAGE_CODE = 'fr-ca'

MAILMAN_WEB_SOCIAL_AUTH = []

SERVE_FROM_DOMAIN = os.environ.get('SERVE_FROM_DOMAIN', 'localhost')

DEFAULT_FROM_EMAIL = 'mailman@' + SERVE_FROM_DOMAIN

ALLOWED_HOSTS = [
    'taralists-mailman-web',
    SERVE_FROM_DOMAIN,
    *filter(None, os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')),
]
