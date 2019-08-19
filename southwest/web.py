import slack
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///bot.sqlite', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)

# sqlalchemy data
class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)
    reservation_number = Column(String(20), unique=False, nullable=False)
    first_name = Column(String(20), unique=False, nullable=False)
    last_name = Column(String(20), unique=False, nullable=False)
    provider = Column(String(20), unique=False, nullable=False)
    provider_id = Column(String(20), unique=False, nullable=False)
    pid = Column(String(20), unique=False, nullable=True)

    def __repr__(self):
        return '<Reservation %r>' % self.reservation_number

    def to_string(self):
        return "{} - {} {}".format(self.reservation_number, self.first_name, self.last_name)

# Returns a text formatted list of checkins for the following user
def checkins_for_user(provider, provider_id):
    session = Session()
    resies = session.query(Reservation).filter_by(provider=provider, provider_id=provider_id).all()
    if len(resies) == 0:
        return "No active reservations"
    return "\n".join([r.to_string() for r in resies])

def delete_by_reservation_id(provider, provider_id, reservation):
    session = Session()
    res = session.query(Reservation).filter_by(provider=provider, provider_id=provider_id, reservation_number=reservation).first()
    session.delete(res)
    session.commit()
    return "Reservation removed"

def handle_slack_message(slack_id, message):
    # if no body, return our current reservations
    if len(message) == 0 or message == 'list':
        return checkins_for_user('slack', slack_id)


    # start a check in
    components = message.split(' ')
    if components[0] in ['remove', 'delete']:
        return delete_by_reservation_id('slack', slack_id, components[1])

    if len(components) < 3:
        return "Not enough parameters"
    session = Session()
    session.add(Reservation(reservation_number=components[0], first_name=components[1], last_name=components[2], provider='slack', provider_id=slack_id))
    session.commit()
    return 'success'

# Slack messages
@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']

    # prevent responding to our own messages
    if 'subtype' in data and data['subtype'] == 'bot_message':
        return

    if 'text' not in data:
        return

    print(data)
    message = data['text']
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user']

    response = handle_slack_message(user, message)

    web_client.chat_postMessage(
        channel=channel_id,
        text=response
        #thread_ts=thread_ts
    )

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    slack.RTMClient(token=os.environ['SLACK_API_TOKEN']).start()
