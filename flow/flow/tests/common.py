import unittest
from flow import ORMSessionBase

class ORMSessionMockup(ORMSessionBase):
    """
    Fake session which holds all results in attributes `added` and `commited`
    """
    def __init__(self):
        self.added = []
        self.commited = []

    def add(self, obj):
        self.added.append(obj)

    def get_or_create(self, model, defaults=None, **kwargs):
        for obj in self.added + self.commited:
            if type(obj) == model:
                found = True
                for field, value in kwargs.items():
                    if getattr(obj, field) != value:
                        found = False
                        break
                if found:
                    return obj, True
        params = kwargs.copy()
        params.update(defaults or {})
        instance = model(**params)
        self.add(instance)
        return instance, False

    def commit(self):
        self.commited.extend(self.added)
        self.added = []


class Book:
    """
    Book model to play with in tests
    """
    def __init__(self, author=None, name=None):
        self.author = author
        self.name = name

    def __eq__(self, rhs):
        if isinstance(rhs, dict):
            return self.author == rhs['author'] and self.name == rhs['name']
        return self.author == rhs.author and self.name == rhs.name


class TestCaseWithData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {'b': 10, 'ced': 100, 'hello': 'world'}
        cls.books = [
            {'author': 'Conan Doyle', 'name': 'Sherlok Holmes'},
            {'author': 'Alexandre Dumas', 'name': 'Les Trois Mousquetaires'},
            {'author': ' J. R. R. Tolkien', 'name': 'The Lord of the Rings'},
        ]
