"""Service fixtures."""

import re
import ssl
from functools import partial
from http.client import HTTPSConnection

import pytest
from pytest_xdocker.compose import ComposeServer, find_compose_files


@pytest.fixture(scope="session")
def env_vars():
    """Environment variables for the services.

    Static because they are persisted in volumes, e.g. database-vol-1.
    """
    server_hostname = "test.local"
    return {
        "DBNAME": "test",
        "DBUSER": "test",
        "DBPASS": "test",
        "HYPERKITTY_API_KEY": "test",
        "SECRET_KEY": "test",
        "SERVER_HOSTNAME": server_hostname,
        "MAILMAN_ADMIN_USER": "admin",
        "MAILMAN_ADMIN_EMAIL": f"admin@{server_hostname}",
        "MAILMAN_ADMIN_PASSWORD": "test",
        "TZ": "UTC",
    }


@pytest.fixture(scope="session")
def env_file(env_vars, request):
    """Environment file containing `env_vars`.

    Cached for troubleshooting purposes.
    """
    env_file = request.config.cache.makedir("taralists") / "env"
    with env_file.open("w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    return env_file


@pytest.fixture(scope="session")
def compose_server(env_file, process, request):
    return partial(
        ComposeServer,
        env_file=env_file,
        compose_files=find_compose_files(request.config.rootdir),
        process=process,
    )


@pytest.fixture(scope="session")
def database_service(compose_server):
    """Database service fixture."""
    server = compose_server("database system is ready to accept connections")
    with server.run("database") as service:
        yield service


@pytest.fixture(scope="session")
def mailman_core_service(compose_server):
    """Mailman-core service fixture."""
    server = compose_server("Directory /opt/mailman/var")
    with server.run("mailman-core") as service:
        yield service


@pytest.fixture(scope="session")
def mailman_web_service(compose_server, mailman_core_service, env_vars):
    """Mailman-web service fixture."""
    server = compose_server(f"Domain {re.escape(env_vars['SERVER_HOSTNAME'])}")
    with server.run("mailman-web") as service:
        yield service


@pytest.fixture(scope="session")
def postfix_service(compose_server):
    """Postfix service fixture."""
    server = compose_server("starting the Postfix mail system")
    with server.run("postfix") as service:
        yield service


@pytest.fixture(scope="session")
def nginx_service(compose_server):
    """Nginx service fixture."""
    server = compose_server("start worker process")
    with server.run("nginx") as service:
        yield service


@pytest.fixture
def nginx_client(nginx_service):
    """Client to the nginx service fixture, over the self-signed dev cert."""
    client = HTTPSConnection(nginx_service.ip, timeout=5, context=ssl._create_unverified_context())  # noqa: S323
    yield client
    client.close()
