import os

import pytest
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def client(postgres_container):
    # Configurar variables de entorno ANTES de importar la app,
    # para que el engine de SQLAlchemy apunte al contenedor de test.
    url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2", "postgresql+psycopg2"
    )
    os.environ["DATABASE_URL"] = url
    os.environ["EVENT_BROKER"] = "memory"
    os.environ["JWT_SECRET"] = "test-secret"

    from app.main import app  # import diferido: requiere las env vars ya seteadas

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    resp = client.post("/auth/login", json={"usuario": "tester"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
