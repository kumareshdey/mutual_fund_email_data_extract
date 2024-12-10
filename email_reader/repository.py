from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime
from typing import Any
from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from db_connection import SessionLocal
from setup import log

class GenericRepository:
    """
    A generic repository class for interacting with SQLAlchemy ORM models.
    Provides common CRUD operations for any table/model.
    """
    def __init__(self, session_factory=SessionLocal):
        self.Session = session_factory

    def add(self, model_instance):
        """
        Add a new record to the database.

        Args:
            model_instance: An instance of the SQLAlchemy model.
        """
        session = self.Session()
        try:
            session.add(model_instance)
            session.commit()
            return model_instance
        except SQLAlchemyError as e:
            session.rollback()
            log.error(f"Error adding record: {e}")
            return None
        finally:
            session.close()

    def add_or_update(self, model_instance):
        """
        Add or update a record in the database.

        Args:
            model_instance: An instance of the SQLAlchemy model.
        """
        session = self.Session()
        try:
            session.merge(model_instance)
            session.commit()
            return model_instance
        except SQLAlchemyError as e:
            session.rollback()
            log.error(f"Error adding or updating record: {e}")
            return None
        finally:
            session.close()

    def get(self, model_class, id_):
        """
        Retrieve a record by primary key.

        Args:
            model_class: The SQLAlchemy model class.
            id_: The primary key of the record to retrieve.
        """
        session = self.Session()
        try:
            return session.query(model_class).get(id_)
        except SQLAlchemyError as e:
            log.error(f"Error retrieving record: {e}")
            return None
        finally:
            session.close()

    def filter(self, model_class, **filters):
        """
        Retrieve records based on filters.

        Args:
            model_class: The SQLAlchemy model class.
            filters: Keyword arguments representing the filter criteria.
        """
        session = self.Session()
        _filters = {}
        for key, value in filters.items():
            if value is not None:
                _filters[getattr(model_class, key)] = value
        try:
            return session.query(model_class).filter_by(**_filters).all()
        except SQLAlchemyError as e:
            log.error(f"Error filtering records: {e}")
            return []
        finally:
            session.close()

    def delete(self, model_class, id_):
        """
        Delete a record by primary key.

        Args:
            model_class: The SQLAlchemy model class.
            id_: The primary key of the record to delete.
        """
        session = self.Session()
        try:
            record = session.query(model_class).get(id_)
            if record:
                session.delete(record)
                session.commit()
                log.info(f"Record with id {id_} deleted successfully.")
            else:
                log.warning(f"Record with id {id_} not found.")
        except SQLAlchemyError as e:
            session.rollback()
            log.error(f"Error deleting record: {e}")
        finally:
            session.close()

def _serialize_value(value: Any) -> Any:
    """
    Handles the serialization of individual attribute values.
    Converts datetime and other special types into JSON-serializable formats.
    
    :param value: The value to serialize
    :return: Serialized value
    """
    if isinstance(value, datetime):
        return value.isoformat()
    return value

def sqlalchemy_to_dict(obj: Any) -> dict:
    """
    Converts an SQLAlchemy model instance into a dictionary.
    
    :param obj: SQLAlchemy model instance
    :return: A dictionary representation of the model instance
    """
    if isinstance(obj.__class__, DeclarativeMeta):
        columns = class_mapper(obj.__class__).columns
        return {
            column.key: _serialize_value(getattr(obj, column.key))
            for column in columns
        }
    elif isinstance(obj, list):  # Handles lists of model instances
        return [sqlalchemy_to_dict(item) for item in obj]
    else:
        raise ValueError(f"Cannot serialize object of type {type(obj)}")

