from typing import Any
from typing import Generic
from typing import Type
from typing import TypeVar

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Generic repository providing common CRUD operations.

    Every repository should inherit from this class.
    """

    def __init__(
        self,
        session: Session,
        model: Type[T],
    ):
        self.session = session
        self.model = model

    # =====================================================
    # CREATE
    # =====================================================

    def save(self, entity: T) -> T:
        """
        Insert or update an entity.
        """
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def create(self, entity: T) -> T:
        return self.save(entity)

    def create_many(self, entities: list[T]) -> list[T]:
        """
        Insert multiple entities.
        """
        if not entities:
            return []

        self.session.add_all(entities)
        self.session.commit()

        return entities

    def bulk_save(self, entities: list[T]) -> list[T]:
        """
        High-performance bulk insert.
        Use for very large imports.
        """
        if not entities:
            return []

        self.session.bulk_save_objects(entities)
        self.session.commit()

        return entities

    # =====================================================
    # READ
    # =====================================================

    def get_by_id(self, entity_id: Any) -> T | None:
        return self.session.get(self.model, entity_id)

    def get_all(self) -> list[T]:
        statement = select(self.model)
        return list(self.session.scalars(statement))

    def get_first(self) -> T | None:
        statement = select(self.model).limit(1)
        return self.session.scalar(statement)

    # =====================================================
    # UPDATE
    # =====================================================

    def update(self, entity: T) -> T:
        return self.save(entity)

    # =====================================================
    # DELETE
    # =====================================================

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
        self.session.commit()

    def delete_by_id(self, entity_id: Any) -> bool:
        entity = self.get_by_id(entity_id)

        if entity is None:
            return False

        self.delete(entity)
        return True

    def delete_all(self) -> int:
        """
        Delete every row for this entity.
        Returns the number of deleted rows.
        """
        deleted = (
            self.session.query(self.model)
            .delete(synchronize_session=False)
        )

        self.session.commit()

        return deleted

    # =====================================================
    # UTILITIES
    # =====================================================

    def count(self) -> int:
        statement = (
            select(func.count())
            .select_from(self.model)
        )

        return self.session.scalar(statement) or 0

    def exists_by_id(self, entity_id: Any) -> bool:
        return self.get_by_id(entity_id) is not None

    # =====================================================
    # SESSION HELPERS
    # =====================================================

    def add(self, entity: T) -> None:
        self.session.add(entity)

    def flush(self) -> None:
        self.session.flush()

    def refresh(self, entity: T) -> None:
        self.session.refresh(entity)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    # =====================================================
    # EXECUTE CUSTOM SQLALCHEMY STATEMENTS
    # =====================================================

    def execute(self, statement):
        return self.session.execute(statement)