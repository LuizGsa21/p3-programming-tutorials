from wtforms.widgets import HiddenInput
from wtforms import IntegerField
from wtforms.validators import Length


class HiddenInteger(IntegerField):
    widget = HiddenInput()


strip_filter = lambda x: x.strip() if x else None


def length_validator(name, min, max):
    return Length(min=min, max=max, message='%s requires %s-%s characters.' % (name, min, max))
