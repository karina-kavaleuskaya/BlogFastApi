from configs.sync_db import Base
from sqlalchemy import (Column, Integer, String, Boolean,
                        TIMESTAMP, text, ForeignKey)
from sqlalchemy.orm import relationship


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    user = relationship('User', back_populates='roles')


class Topics(Base):
    __tablename__ = 'topics'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)

    posts = relationship('Post', back_populates='topics')



class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    content = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='posts')
    topics = relationship('Topics', back_populates='posts')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    second_name = Column(String, nullable=False)
    nickname = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), default=1)
    banned_is = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))

    posts = relationship('Post', back_populates='user')
    roles = relationship('Roles', back_populates='user')
    subscriptions = relationship('Subscription',
                                 foreign_keys='Subscription.subscriber_id',
                                 backref='subscriber')
    subscribers = relationship('Subscription',
                               foreign_keys='Subscription.subscribed_id',
                               backref='subscribed')


class Subscription(Base):
    __tablename__ = 'subscription'
    subscriber_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    subscribed_id = Column(Integer, ForeignKey('user.id'), primary_key=True)