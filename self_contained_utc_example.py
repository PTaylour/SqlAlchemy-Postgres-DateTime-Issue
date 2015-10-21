from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types
from pytz import utc

# setup typical flask-sqlalchemy enabled app
app = Flask(__name__)
app.config.update(
  SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost:5432/test'
  SQLALCHEMY_ECHO = False
  SECRET_KEY = 'a-secret-key'
  DEBUG = True
)
db = SQLAlchemy(app)

# custom datetime type
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

# model that uses UTCDateTime
class EventUTC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(UTCDateTime)

    def events_before(self):
      
        return EventUTC.query.filter(
            (EventUTC.timestamp <= self.timestamp)
        ).all()


def create_sample_events():
    db.drop_all()
    db.create_all()
    # create some utc events
    now = datetime.utcnow().replace(tzinfo=utc)
    events = [
        EventUTC(timestamp=now + timedelta(minutes=t))
        for t in range(-2, 1)
    ]
    for ev in events: db.session.add(ev)
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
    create_sample_events()
    all_utc_event = EventUTC.query.all()
  
    # 'for each test event,'
    # 'fetch all events that occur before (or at the same time)'
    # 'Using tz aware datetimes'
    # 'fails when using postgres, succeeds for sqlite'
    map(test_filter_query, all_utc_event)
