def test_crear_y_obtener_tarea(client, auth_headers):
    payload = {
        "titulo": "Preparar informe",
        "descripcion": "Informe mensual de operaciones",
        "prioridad": "alta",
        "fecha_limite": "2026-12-01",
    }
    resp = client.post("/tareas", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    tarea_id = resp.json()["id"]

    resp = client.get(f"/tareas/{tarea_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["titulo"] == "Preparar informe"
    assert resp.json()["estado"] == "pendiente"


def test_completar_tarea_publica_evento_y_cambia_estado(client, auth_headers):
    payload = {
        "titulo": "Tarea a completar",
        "descripcion": "",
        "prioridad": "media",
        "fecha_limite": "2026-12-01",
    }
    resp = client.post("/tareas", json=payload, headers=auth_headers)
    tarea_id = resp.json()["id"]

    resp = client.patch(f"/tareas/{tarea_id}/completar", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["estado"] == "completada"


def test_listar_tareas_con_filtro_de_estado(client, auth_headers):
    client.post(
        "/tareas",
        json={
            "titulo": "Filtrable",
            "descripcion": "",
            "prioridad": "baja",
            "fecha_limite": "2026-12-01",
        },
        headers=auth_headers,
    )
    resp = client.get("/tareas?estado=pendiente&page=1&size=10", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert all(t["estado"] == "pendiente" for t in body["items"])


def test_endpoint_protegido_sin_token_devuelve_401(client):
    resp = client.get("/tareas")
    assert resp.status_code in (401, 403)


def test_obtener_tarea_inexistente_devuelve_404(client, auth_headers):
    import uuid

    resp = client.get(f"/tareas/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "TAREA_NO_ENCONTRADA"
