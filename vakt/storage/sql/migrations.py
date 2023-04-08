from sqlalchemy import Column, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base

from .model import Base
from ..migration import Migration, MigrationSet

MigrationBase = declarative_base()


class MigrationModel(MigrationBase):
    """
        Migration version storage
    """

    __tablename__ = 'vakt_migrations'

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)


class SQLMigrationSet(MigrationSet):
    """
        Set of migrations for SQL Storage
    """

    def __init__(self, storage):
        self.storage = storage
        self.session = storage.session
        self._index = 1

        MigrationModel.metadata.create_all(self.storage.session.bind)

    def migrations(self):
        return [Migration0To1x3x0(self.storage)]

    def save_applied_number(self, number):
        try:
            data = self.session.get(MigrationModel, self._index)
            # Insert if entry not found else update
            if not data:
                data = MigrationModel(id=self._index, version=number)
                self.session.add(data)
            else:
                data.version = number
            self.session.commit()
        except SQLAlchemyError as err:
            self.session.rollback()
            raise err

    def last_applied(self):
        data = self.session.get(MigrationModel, self._index)
        if data:
            return data.version
        return 0


class Migration0To1x3x0(Migration):
    """
        Migration between versions 0 and 1.3.0.
        This migration is initial.
    """

    def __init__(self, storage):
        self.storage = storage

    @property
    def order(self):
        return 1

    def up(self):
        Base.metadata.create_all(self.storage.session.bind)

    def down(self):
        Base.metadata.drop_all(self.storage.session.bind)
