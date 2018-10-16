from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    posts = relationship("Post", back_populates="user")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<User(id={}, name='{}')>".format(self.id, self.name)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    post = relationship("Post", secondary=lambda: post_tags_table, back_populates="tags")

    def __repr__(self):
        return "<Tag(id={}, name='{}')>".format(self.id, self.name)


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    content = Column(String)
    guid = Column(String, unique=True)
    title = Column(String)
    link = Column(String)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    tags = relationship("Tag", secondary=lambda: post_tags_table, back_populates="post")
    user = relationship("User", uselist=False)

    def __repr__(self):
        return "<Tag(id={}, name='{}'".format(self.id, self.name)


post_tags_table = Table('post_tags',
                        Base.metadata,
                        Column('post_id', Integer, ForeignKey("posts.id"), primary_key=True),
                        Column('tag_id', Integer, ForeignKey("tags.id"), primary_key=True))
