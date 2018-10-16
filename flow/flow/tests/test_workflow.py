import unittest
from flow import FieldsTransform, ModelObjectCreate, Root
from .common import *


class ForEachUpperCaseTest(TestCaseWithData):
    def test_for_each_upper_case(self):
        a = Root().for_each(FieldsTransform({'name': str.upper})).root
        transformed_books = a(self.books)
        for book_dict, transformed_book_dict in zip(self.books, transformed_books):
            self.assertEqual(book_dict['name'].upper(), transformed_book_dict['name'])


class ForEachToModelTest(TestCaseWithData):
    def test_for_each_to_model(self):
        session = ORMSessionMockup()
        a = Root().for_each(ModelObjectCreate(Book, unique=['name', 'author'])).root
        with session:
            # check for uniqueness also
            a(self.books + self.books)
        self.assertEqual(self.books, session.commited)
