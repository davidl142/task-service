from datetime import date

import pytest

from app.domain.task import EstadoTarea, Prioridad, Tarea, TransicionInvalidaError


def _tarea(**kwargs):
    defaults = dict(
        titulo="Revisar reporte",
        descripcion="Revisar el reporte mensual",
        prioridad=Prioridad.ALTA,
        fecha_limite=date(2026, 12, 31),
    )
    defaults.update(kwargs)
    return Tarea(**defaults)


def test_tarea_inicia_pendiente():
    tarea = _tarea()
    assert tarea.estado == EstadoTarea.PENDIENTE


def test_completar_tarea_cambia_estado():
    tarea = _tarea()
    tarea.completar()
    assert tarea.estado == EstadoTarea.COMPLETADA


def test_completar_tarea_ya_completada_lanza_error():
    tarea = _tarea()
    tarea.completar()
    with pytest.raises(TransicionInvalidaError):
        tarea.completar()


def test_actualizar_tarea_cambia_solo_campos_dados():
    tarea = _tarea()
    original_descripcion = tarea.descripcion
    tarea.actualizar(titulo="Nuevo título")
    assert tarea.titulo == "Nuevo título"
    assert tarea.descripcion == original_descripcion
