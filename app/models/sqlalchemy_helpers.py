from sqlalchemy.ext.hybrid import Comparator, hybrid_property
from sqlalchemy.sql import func
from app.extensions import db
from flask_login import UserMixin


class CaseInsensitiveWord(Comparator):
    """Hybrid value representing a lower case representation of a word."""

    def __init__(self, word):
        if isinstance(word, basestring):
            self.word = word.lower()
        elif isinstance(word, CaseInsensitiveWord):
            self.word = word.word
        else:
            self.word = func.lower(word)

    def operate(self, op, other):
        if not isinstance(other, CaseInsensitiveWord):
            other = CaseInsensitiveWord(other)
        return op(self.word, other.word)

    def __clause_element__(self):
        return self.word

    def __str__(self):
        return self.word


class DefaultUserMixin(UserMixin):

    @property
    def username(self):
        raise NotImplementedError

    @property
    def email(self):
        raise NotImplementedError

    @property
    def firstName(self):
        raise NotImplementedError

    @property
    def lastName(self):
        raise NotImplementedError

    @property
    def isAdmin(self):
        raise NotImplementedError


    @hybrid_property
    def fullname(self):
        fullname = ''
        if isinstance(self.firstName, basestring):
            fullname = self.firstName
        if isinstance(self.lastName, basestring):
            fullname += ' ' + self.lastName
        return fullname

    @hybrid_property
    def username_insensitive(self):
        return self.username.lower()

    @username_insensitive.comparator
    def username_insensitive(self):
        return CaseInsensitiveWord(self.username)

    @hybrid_property
    def email_insensitive(self):
        return self.email.lower()

    @email_insensitive.comparator
    def email_insensitive(self):
        return CaseInsensitiveWord(self.email)

    def is_admin(self):
        return self.isAdmin


# monkey patch to db.Model. used as a convenience method for populating values from a wtform
def populate_from_form(model, form):
    fields = form.data
    for column, value in fields.items():
        if hasattr(model, column):
            setattr(model, column, value)

setattr(db.Model, 'populate_from_form', populate_from_form)