"""Integration tests for the nginx service."""

from http.client import HTTPConnection


def test_nginx_redirects_http_to_https(nginx_service):
    """The nginx service should redirect HTTP to HTTPS."""
    client = HTTPConnection(nginx_service.ip, timeout=5)
    client.request("GET", "/hyperkitty/")
    response = client.getresponse()

    assert response.status == 301
    assert response.headers["location"] == f"https://{nginx_service.ip}/hyperkitty/"


def test_nginx_proxies_mailman_web(nginx_client):
    """The nginx service should proxy HyperKitty from mailman-web."""
    nginx_client.request("GET", "/hyperkitty/")
    response = nginx_client.getresponse()

    assert response.status == 200
    assert "text/html" in response.headers["content-type"]


def test_nginx_status(nginx_client):
    """The nginx service should expose its status to private networks."""
    nginx_client.request("GET", "/nginx_status")
    response = nginx_client.getresponse()

    assert response.status == 200
    assert b"Active connections" in response.read()
