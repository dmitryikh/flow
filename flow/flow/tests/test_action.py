import unittest
from flow import Action, GetField, FieldsTransform, Lambda, ModelObjectCreate
from .common import *


class AbstractActionTest(TestCaseWithData):
    def test_action_init(self):

        class MyAction(Action):
            pass

        for class_ in [Action, MyAction]:
            self.assertRaisesRegex(TypeError, r"Can't instantiate abstract class", class_)


class GetFieldTest(unittest.TestCase):
    def test_field_access(self):
        d = {'b': 10, 'ced': 100}
        self.assertRaises(KeyError, GetField(''), d)
        self.assertEqual(GetField('b')(d), 10)
        self.assertEqual(GetField('ced')(d), 100)

    def test_empty_init(self):
        self.assertRaises(TypeError, r"__init__() missing 1 required positional argument: 'field'", GetField)


class FieldTransformTest(TestCaseWithData):
    def test_empty_transformations(self):
        a = FieldsTransform({})
        self.assertEqual(self.data, a(self.data))

    def test_transformations(self):
        a = FieldsTransform({'b': lambda x: x * 20, 'hello': str.upper})
        d_true = self.data.copy()
        d_true['b'] = d_true['b'] * 20
        d_true['hello'] = d_true['hello'].upper()
        self.assertEqual(d_true, a(self.data))

    def test_transformations_lambda(self):
        a = FieldsTransform({'b': Lambda(lambda x: x * 20), 'hello': Lambda(str.upper)})
        d_true = self.data.copy()
        d_true['b'] = d_true['b'] * 20
        d_true['hello'] = d_true['hello'].upper()
        self.assertEqual(d_true, a(self.data))

class LambdaTest(TestCaseWithData):
    def test_non_callable(self):
        for arg in [{}, [1, 'abc'], 'string']:
            self.assertRaisesRegex(ValueError, r"expected func to be callable object, got type", Lambda, arg)

    def test_callable(self):
        a = Lambda(int)
        self.assertEqual(10, a('10'))

        def do_strange(not_used):
            return 'my_answer'

        self.assertEqual('my_answer', Lambda(do_strange)('10'))


class ModelObjectCreateTest(TestCaseWithData):
    def test_without_session(self):
        a = ModelObjectCreate(Book)
        self.assertRaisesRegex(RuntimeError, r"expected session object in threading.local()", a, self.data)

    def test_non_existent_attribute(self):
        d = self.books[0].copy()
        d['non_existent_field'] = 'some data'
        with ORMSessionMockup():
            self.assertRaisesRegex(ValueError, r"model Book doesn't have attribute non_existent_field", ModelObjectCreate(Book), d)
            self.assertRaisesRegex(ValueError, r"model Book doesn't have attribute another", ModelObjectCreate(Book, fields=['name', 'another']), d)

    def test_non_existent_field(self):

        class BookEx(Book):
            def __init__(self, year=None, **kwargs):
                super(BookEx, self).__init__(**kwargs)
                self.year = year

        with ORMSessionMockup():
            self.assertRaisesRegex(KeyError, r"data doesn't have key 'year'", ModelObjectCreate(BookEx, fields=['year']), self.books[0])

    def test_default_fields(self):
        session = ORMSessionMockup()
        with session:
            a = ModelObjectCreate(Book)
            for book in self.books:
                a(book)
        self.assertEqual(self.books, session.commited)

    def test_duplicates(self):
        session = ORMSessionMockup()
        with session:
            a = ModelObjectCreate(Book)
            for book in self.books + self.books:
                a(book)
        # twice duplicated books in commited list
        self.assertEqual(self.books + self.books, session.commited)

    def test_unique(self):
        session = ORMSessionMockup()
        with session:
            a = ModelObjectCreate(Book, unique=['name', 'author'])
            for book in self.books:
                a(book)
            for book in self.books:
                a(book)
        # only unique books in commited list
        self.assertEqual(self.books, session.commited)

    def test_fields(self):
        session = ORMSessionMockup()
        with session:
            a = ModelObjectCreate(Book, fields=['name'])
            for book in self.books:
                a(book)
        # only name field is set
        for obj in session.commited:
            self.assertTrue(obj.name is not None)
            self.assertTrue(obj.author is None)

    def test_fields_map(self):

        # parse data to another model
        class MyFavoriteBook:
            def __init__(self, favorite_name=None):
                self.favorite_name = favorite_name

        session = ORMSessionMockup()
        with session:
            a = ModelObjectCreate(MyFavoriteBook, fields=['favorite_name'], fields_map={'favorite_name': 'name'})
            for book in self.books:
                a(book)
        # check than name is correctly set
        for obj, book_dict in zip(session.commited, self.books):
            self.assertEqual(obj.favorite_name, book_dict['name'])
