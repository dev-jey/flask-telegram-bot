"""Data models."""
from application.factory import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
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
    activated = db.Column(
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

    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Message(db.Model):
    """Data model for running messages."""

    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    message = db.Column(
        db.Text,
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

    name = db.Column(
        db.Text,
        index=False,
        unique=False,
        nullable=False
    )

    owner = db.Column(
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
