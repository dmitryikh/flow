import feedparser
from flow import ORMSessionSQLAlchemy
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import time
import unittest
from ..model import Base, Tag, Post, User
from ..workflow import feed_extractor


class RssFeedTest(unittest.TestCase):
    def read_xml(self, filename):
        f = open(filename)
        document = feedparser.parse(f.read())
        f.close()
        return document

    def test_rss_feed(self):
        doc1 = self.read_xml(os.path.join(os.path.dirname(__file__), 'data', 'habr_part1.xml'))
        doc2 = self.read_xml(os.path.join(os.path.dirname(__file__), 'data', 'habr_part2.xml'))

        engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        session = Session()

        # parse doc1 and check DB state
        with ORMSessionSQLAlchemy(session):
            feed_extractor(doc1)

        tag_names = [tag.name for tag in session.query(Tag).order_by(Tag.id)]
        true_tag_names = [
            'Расширения для браузеров', 'Клиентская оптимизация',
            'Мультикоптеры', 'доставка', 'бургеры', 'дроны',
            'исландия', 'рейкьявик', 'Open source', 'Node.JS',
        ]
        self.assertEqual(tag_names, true_tag_names)

        user_names = [user.name for user in session.query(User).order_by(User.id)]
        true_user_names = ['altrus', 'SLY_G', 'Batin']
        self.assertEqual(user_names, true_user_names)

        post_titles = [post.title for post in session.query(Post).order_by(Post.id)]
        true_post_titles = [
            'Улучшаем интернет программы',
            '[Перевод] Оправдана ли коммерческая доставка дронами? В Исландии собираются это выяснить',
            'Cogear.JS – современный генератор статических сайтов',
            'Новости о борьбе со старением',
        ]
        self.assertEqual(post_titles, true_post_titles)

        post_user_names = [post.user.name for post in session.query(Post).order_by(Post.id)]
        true_post_user_names = ['altrus', 'SLY_G', 'SLY_G', 'Batin']
        self.assertEqual(post_user_names, true_post_user_names)

        post_tag_names = [[tag.name for tag in post.tags] for post in session.query(Post).order_by(Post.id)]
        true_post_tag_names = [
            ['Расширения для браузеров', 'Клиентская оптимизация'],
            ['Расширения для браузеров', 'Мультикоптеры', 'доставка', 'бургеры', 'дроны', 'исландия', 'рейкьявик'],
            ['Open source', 'Node.JS'],
            ['Open source'],
        ]
        self.assertEqual(post_tag_names, true_post_tag_names)

        # parse doc2 and check DB state
        with ORMSessionSQLAlchemy(session):
            feed_extractor(doc2)

        tag_names = [tag.name for tag in session.query(Tag).order_by(Tag.id)]
        true_tag_names += [
            'Геоинформационные сервисы', 'Научно-популярное', 'Здоровье гика',
            'борьба со старением', 'продление жизни', 'трансгуманизм', 'Математика', 'Python',
        ]
        self.assertEqual(tag_names, true_tag_names)

        user_names = [user.name for user in session.query(User).order_by(User.id)]
        true_user_names += ['Sergey', 'helenblack']
        self.assertEqual(user_names, true_user_names)

        post_titles = [post.title for post in session.query(Post).order_by(Post.id)]
        true_post_titles += [
            'Символьное решение линейных дифференциальных уравнений и систем методом преобразований Лапласа c применением SymPy',
        ]
        self.assertEqual(post_titles, true_post_titles)

        # check that users are updated and new added
        post_user_names = [post.user.name for post in session.query(Post).order_by(Post.id)]
        true_post_user_names = ['altrus', 'SLY_G', 'SLY_G', 'Sergey', 'helenblack']
        self.assertEqual(post_user_names, true_post_user_names)

        # check that tags are changed on updated posts and new added
        post_tag_names = [[tag.name for tag in post.tags] for post in session.query(Post).order_by(Post.id)]
        true_post_tag_names = [
            ['Расширения для браузеров', 'Клиентская оптимизация'],
            ['Мультикоптеры', 'Геоинформационные сервисы'],
            ['Open source', 'Node.JS'],
            ['Научно-популярное', 'Здоровье гика', 'борьба со старением', 'продление жизни', 'трансгуманизм'],
            ['Математика', 'Python'],
        ]
        self.assertEqual(post_tag_names, true_post_tag_names)
