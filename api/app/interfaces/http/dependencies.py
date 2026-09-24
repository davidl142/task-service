from fastapi import Depends
from sqlalchemy.orm import Session

from app.domain.ports import EventPublisher, TaskRepository
from app.infrastructure.db.repository import SqlAlchemyTaskRepository
from app.infrastructure.db.session import get_db
from app.infrastructure.events.publishers import build_event_publisher

_publisher_singleton: EventPublisher | None = None


def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    return SqlAlchemyTaskRepository(db)


def get_event_publisher() -> EventPublisher:
    global _publisher_singleton
    if _publisher_singleton is None:
        _publisher_singleton = build_event_publisher()
    return _publisher_singleton
