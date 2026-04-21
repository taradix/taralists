"""Integration tests for the mailman-web service."""

import json
import urllib.error
import urllib.request
from email.message import EmailMessage

import pytest
from pytest_xdocker.retry import retry


def _hyperkitty_url(mailman_web_service, path):
    return f"http://{mailman_web_service.ip}:8000/hyperkitty/{path}"


def test_mailman_web_http(mailman_web_service):
    """Mailman-web should respond to HTTP requests on port 8000."""
    def connect():
        req = urllib.request.Request(_hyperkitty_url(mailman_web_service, ""))
        with urllib.request.urlopen(req) as resp:
            return resp.status

    status = retry(connect).catching(urllib.error.URLError)
    assert status == 200


def test_mailman_web_requires_auth(mailman_web_service, env_vars):
    """HyperKitty archiver API should reject requests without auth."""
    req = urllib.request.Request(
        _hyperkitty_url(mailman_web_service, f"api/mailman/urls?mlist=test@{env_vars['SERVER_HOSTNAME']}"),
    )
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req)
    assert exc_info.value.code == 401


def test_mailman_web_urls(mailman_web_service, env_vars):
    """HyperKitty should return an archive URL for a mailing list."""
    def get_url():
        req = urllib.request.Request(
            _hyperkitty_url(mailman_web_service, f"api/mailman/urls?mlist=test@{env_vars['SERVER_HOSTNAME']}"),
            headers={"Authorization": f"Token {env_vars['HYPERKITTY_API_KEY']}"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    result = retry(get_url).catching(urllib.error.URLError)
    assert "url" in result


def test_mailman_web_archive(mailman_web_service, env_vars):
    """HyperKitty should archive a message via the mailman API."""
    msg = EmailMessage()
    msg["Subject"] = "Integration test"
    msg["From"] = f"sender@{env_vars['SERVER_HOSTNAME']}"
    msg["To"] = f"test@{env_vars['SERVER_HOSTNAME']}"
    msg["Message-ID"] = "<test-archive-001@test.local>"
    msg["Date"] = "Thu, 17 Apr 2026 00:00:00 +0000"
    msg.set_content("Integration test message body.")
    message_bytes = msg.as_bytes()

    boundary = "testboundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="mlist"\r\n'
        f"\r\n"
        f"test@{env_vars['SERVER_HOSTNAME']}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="message"; filename="message.txt"\r\n'
        f"Content-Type: application/octet-stream\r\n"
        f"\r\n"
    ).encode() + message_bytes + f"\r\n--{boundary}--\r\n".encode()

    def archive():
        req = urllib.request.Request(
            _hyperkitty_url(mailman_web_service, "api/mailman/archive"),
            data=body,
            headers={
                "Authorization": f"Token {env_vars['HYPERKITTY_API_KEY']}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    result = retry(archive).catching(urllib.error.URLError)
    assert "url" in result
