#!/usr/bin/env python3
import os
from mailmanclient import Client

domain = os.environ.get('SERVE_FROM_DOMAIN', '')
if not domain:
    raise SystemExit('SERVE_FROM_DOMAIN is not set')

client = Client(
    os.environ.get('MAILMAN_REST_API_URL', 'http://mailman-core:8001/3.1/'),
    os.environ.get('MAILMAN_REST_API_USER', 'restadmin'),
    os.environ.get('MAILMAN_REST_API_PASS', 'restpass'),
)

if domain not in [d.mail_host for d in client.domains]:
    client.create_domain(domain)
    print('Domain {} created'.format(domain))
else:
    print('Domain {} already exists'.format(domain))
