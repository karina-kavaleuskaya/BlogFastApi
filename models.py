from db.sync_db import Base
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

class Country(Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    user = relationship('User', back_populates='country')


class Sex(Base):
    __tablename__ = 'sex'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    user = relationship('User', back_populates='sex')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    content = Column(String, nullable=False)
    file_path = Column(String)
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
    sex_id = Column(Integer, ForeignKey('sex.id'))
    country_id = Column(Integer, ForeignKey('country.id'))

    posts = relationship('Post', back_populates='user')
    roles = relationship('Roles', back_populates='user')
    subscriptions = relationship('Subscription',
                                 foreign_keys='Subscription.subscriber_id',
                                 backref='subscriber')
    subscribers = relationship('Subscription',
                               foreign_keys='Subscription.subscribed_id',
                               backref='subscribed')

    tokens = relationship('Tokens', back_populates='user')
    sex = relationship('Sex', back_populates='user')
    country = relationship('Country', back_populates='user')


class Subscription(Base):
    __tablename__ = 'subscription'

    subscriber_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    subscribed_id = Column(Integer, ForeignKey('user.id'), primary_key=True)


class Tokens(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    reset_token = Column(String, nullable=False)
    reset_token_expire = Column(TIMESTAMP, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship('User', back_populates='tokens')