from abc import ABC, abstractmethod
import threading

# used to hold global session
_thread_local_storage = threading.local()


class ORMSessionBase(ABC):
    """ORMSessionBase base class wraps work with particular ORM framework

    To support different ORM framework one should inherit class from ORMSessionBase and define it's abstract methods.
    See detail in methods docs.


    Exmaple
    -------
    To run `data` processing with `workflow` actions with ORM session do the next:
    > with SomeInheritedORMSession(session):
    >     worflow(data)
    """
    @abstractmethod
    def add(self, obj):
        """
        Add ORM object `obj` to the session

        Parameters
        ----------
        obj : ORM object
        """

    @abstractmethod
    def get_or_create(self, model, defaults=None, **kwargs):
        """
        Search in DB objects with type `model` with fields `kwargs`.
        Return one if found or create new witt fields from `kwargs` and `defaults`

        Parameters
        ----------
        model : ORM model class
        defaults : dict - fields to be set if new object is created
        kwargs : dict - fields to be searched in DB
        """

    @abstractmethod
    def commit(self):
        """Commit changes to the DB"""

    def __enter__(self):
        _thread_local_storage.session = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _thread_local_storage.__dict__.pop('session', None)
        if exc_val:
            raise
        self.commit()


class ORMSessionSQLAlchemy(ORMSessionBase):
    """ORMSession realisation for SQLAlchemy"""
    def __init__(self, session):
        """
        Parameters
        ----------
        session : SQLAlchemy's session object
        """
        self.session = session

    def add(self, obj):
        self.session.add(obj)

    def get_or_create(self, model, defaults=None, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            params = kwargs.copy()
            params.update(defaults or {})
            instance = model(**params)
            self.add(instance)
            return instance, True

    def commit(self):
        self.session.commit()
