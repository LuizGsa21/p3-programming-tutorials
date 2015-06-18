
from jinja2 import Markup


class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    # parse utc to local time
    # moment(moment.utc("%s").toDate()

    def render(self, format):
        return Markup('<script>document.write(moment(moment.utc("%s").toDate()).%s);</script>' % (self.timestamp, format))

    def format(self, fmt):
        return self.render('format("%s")' % fmt)

    def calendar(self):
        return self.render('calendar()')

    def fromNow(self):
        return self.render('fromNow()')
