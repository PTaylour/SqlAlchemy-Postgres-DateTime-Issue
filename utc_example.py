from datetime import datetime, timedelta
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types
from pytz import utc


app = Flask(__name__)
app.config.from_pyfile('hello.cfg')
db = SQLAlchemy(app)

class UTCDateTime(types.TypeDecorator):
    """ decorator to enforce tz aware DateTime.
        http://stackoverflow.com/questions/79797/how-do-i-convert-local-time-to-utc-in-python
    """
    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(utc)

    def process_result_value(self, value, engine):
        if value is not None:
            return value.replace(tzinfo=utc)


class EventNaive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)

    def events_before(self):
        return EventNaive.query.filter(
            (EventNaive.timestamp <= self.timestamp)
        ).all()

class EventUTC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(UTCDateTime)

    def events_before(self):
        return EventUTC.query.filter(
            (EventUTC.timestamp <= self.timestamp)
        ).all()

def setup():
    db.drop_all()
    db.create_all()

    # create some utc events
    now = datetime.utcnow().replace(tzinfo=utc)
    events = [
        EventUTC(timestamp=now + timedelta(minutes=t))
        for t in range(-2, 1)
    ]
    for ev in events: db.session.add(ev)
    

    # create some naive events
    now.replace(tzinfo=None)
    events = [
        EventNaive(timestamp=now + timedelta(minutes=t))
        for t in range(-2, 1)
    ]
    for ev in events: 
        db.session.add(ev)

    db.session.commit()


def check_timestamp_is_before(candidate, timestamp):
    print 'evaluating: ', candidate.timestamp, ' <= ', timestamp
    if not (candidate.timestamp <= timestamp):
        print '^^^ failed'

def test_filter_query(event):
    events_before =  event.events_before()
    print 'test for event with timestamp: ', event.timestamp
    for test_ev in events_before:
        check_timestamp_is_before(test_ev, event.timestamp)
    print '\n'



if __name__ == '__main__':
    setup()


    all_naive = EventNaive.query.all()
    all_utc = EventUTC.query.all()

    print 'fetch events before an event for all events'
    print 'Using Naive Datatimes and then tz aware datetimes'
    print '\n\ntesting with naive:\n'    
    map(test_filter_query, all_naive)
    print '\n\ntesting with utc:\n'    
    map(test_filter_query, all_utc)


