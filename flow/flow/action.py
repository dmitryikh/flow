from abc import ABC, abstractmethod
import threading
from .session import _thread_local_storage


class Action(ABC):
    """Action base class

    Action represents a basic action on data. All child action classes must
    define `do` method which do actual work. User should call `__call__`
    method to perform actions. Actions can be chained by `then` and/or
    `for_each` methods.

    Attributes
    ----------
    next_action : Action
        action to be called next, could be None
    for_each : Action
        action to be called on each element of data, could be None. Data must be iterable.
    root : Action
        root stores a pointer to root action of a workflow
    """

    def __init__(self):
        self.next_action = None
        self.for_each_action = None
        self.root = self

    def then(self, action):
        """Attach `action` as next action"""
        self.next_action = action
        action.root = self.root
        return action

    def for_each(self, action):
        """Attach `action` as for_each action"""
        self.for_each_action = action
        action.root = self.root
        return action

    @abstractmethod
    def do(self, data):
        """All actions should expose `do` method to do actual work

        Parameters
        ----------
        data : any - argument to action

        Returns
        -------
        any
            return value of the action
        """

    def __call__(self, data):
        """Wrapper around `do` to perfarm all registered action. User should call this method instead of `do` directly

        Parameters
        ----------
        data : any - argument to action

        Returns
        -------
        any
            return value of the action
        """
        ret = self.do(data)
        if self.for_each_action is not None:
            ret2 = []
            for item in ret:
                ret2.append(self.for_each_action(item))
            ret = ret2

        if self.next_action is not None:
            return self.next_action(ret)
        else:
            return ret


class Root(Action):
    """Action that do nothing. Useful as first action:
           > Root().for_each(usef_action)
    """
    def do(self, data):
        return data


class Debug(Action):
    """Debug prints its argument without transformations"""

    def __init__(self):
        super(Debug, self).__init__()

    def do(self, data):
        print(data)
        return data


class GetField(Action):
    """GetField prints its argument without transformations"""

    def __init__(self, field):
        super(GetField, self).__init__()
        self.field = field

    def do(self, data):
        return data[self.field]


class FieldsTransform(Action):
    """Perform actions on particular data fields and put result back"""

    def __init__(self, transformations):
        """
        Parameters
        ----------
        transformations : dict - keys: data fields to transform, values: actions on data fields
            actions can be Action objects or any callable

        Example
        -------
        >>> FieldsTransform({'name': lambda x: x.upper(),
                             'age': Debug()}).then(Debug())
        """
        super(FieldsTransform, self).__init__()
        self.transformations = {}
        for field, action in transformations.items():
            if issubclass(type(action), Action):
                self.transformations[field] = action
            elif callable(action):
                self.transformations[field] = Lambda(action)
            else:
                raise ValueError('unexpected type of action (got {})'.format(type(action)))

    def do(self, data):
        for key, transformation in self.transformations.items():
            data[key] = transformation(data[key])
        return data

    def sub_actions(self):
        return [(k, v) for k, v in self.transformations.items()]


class Lambda(Action):
    """Wraps any callable object as Action"""

    def __init__(self, func):
        super(Lambda, self).__init__()
        if not callable(func):
            raise ValueError("expected func to be callable object, got type '{}'".format(type(func)))
        self.func = func

    def do(self, data):
        return self.func(data)


class ModelObjectCreate(Action):
    """ModelObjectCreate fills ORM model object and add it to current session"""

    def __init__(self, orm_model, fields=None, unique=None, fields_map=None):
        """
        Parameters
        ----------
        orm_model : class - class of the model to fill
        fields : list - orm_model attributes to set.
            If `fields` is None than all data fields will be added to `orm_model` instance
        fields_map : dict - key: orm_model field, value: data field. `fields_map` is used when orm and data fields differ.
        unique : list - orm_model fields to ne unique in DB. If mode object with such fields alreade exist in DB then
            it will be changed instead of creating duplicate

        Example
        -------
        >>> ModelObjectCreate(orm_model=Post,
                              fields=['title', 'id', 'link', 'date', 'author', 'tags'],
                              fields_map={'date': 'published_parsed', 'user': 'author'},
                              unique=['id'])
        """
        super(ModelObjectCreate, self).__init__()
        self.orm_model = orm_model
        self.unique = unique
        self.fields_map = fields_map if fields_map is not None else {}
        self.fields = fields

    def do(self, data):
        """Perform actual mapping of data fields into orm model.

        ORM session are taken from ORMSessionBase context.

        Parameters
        ----------
        data : dict object or single value - if dict is single value and `fields` contains only one field,
            then the value set to appropriate `orm_model` instanse field

        Returns
        ------
        filledt `orm_model` instance alredy added to the session
        """
        fields = self.fields
        session = getattr(_thread_local_storage, 'session', None)
        if session is None:
            raise RuntimeError("expected session object in threading.local(). "
                               "Do you forget to wrap call with ORMSessionBase context?")
        if fields is None:
            fields = list(data.keys())
        if not isinstance(data, dict):
            if len(fields) != 1:
                raise ValueError('got single value data ({}), but fields has {} elements'.format(data, len(fields)))
            data = {fields[0]: data}

        if self.unique is not None:
            obj, _ = session.get_or_create(self.orm_model,
                                           **{field: data[self.fields_map.get(field, field)] for field in self.unique})
        else:
            obj = self.orm_model()
            session.add(obj)
        for field in fields:
            if not hasattr(obj, field):
                raise ValueError("model {} doesn't have attribute {}".format(self.orm_model.__name__, field))
            data_key = self.fields_map.get(field, field)
            if data_key not in data:
                raise KeyError("data doesn't have key '{}' (got: {})".format(data_key, data))
            setattr(obj, field, data[data_key])

        return obj
