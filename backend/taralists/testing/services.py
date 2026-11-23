"""Service fixtures."""

import re
from functools import partial

import pytest
from pytest_xdocker.compose import ComposeServer, find_compose_files


@pytest.fixture(scope="session")
def project():
    return "test"


@pytest.fixture(scope="session")
def env_vars(project):
    """Environment variables for the services.

    Static because they are persisted in volumes, e.g. database-vol-1.
    """
    server_hostname = "test.local"
    return {
        "COMPOSE_PROJECT_NAME": project,
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
def compose_files(request):
    return find_compose_files(request.config.rootdir)


@pytest.fixture(scope="session")
def compose_server(project, env_file, compose_files, process):
    return partial(
        ComposeServer,
        project=project,
        env_file=env_file,
        compose_files=compose_files,
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
