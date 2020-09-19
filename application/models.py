"""Data models."""
from application.factory import db


class User(db.Model):
    """Data model for user accounts."""

    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False
    )
    email = db.Column(
        db.String(80),
        index=True,
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.Text,
        index=False,
        unique=False,
        nullable=True
    )
    created = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=False
    )
    admin = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False
    )
    active = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False
    )

    paid = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Process(db.Model):
    """Data model for running processes."""

    __tablename__ = 'processes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    message = db.Column(
        db.String(64),
        index=False,
        unique=False,
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=False
    )   

    iterations = db.Column(
        db.Integer,
        index=False,
        unique=False,
        nullable=False
    )

    link= db.Column(
        db.String(64),
        index=False,
        unique=False,
        nullable=False
    )

    owner =  db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    on = db.Column(
        db.Boolean,
        index=False,
        unique=False,
        nullable=False
    )

    created = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=False
    )
    
    def __repr__(self):
        return '<PID: {}>'.format(self.id)