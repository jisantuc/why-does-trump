import os
import random
from requests import Session
from requests_oauthlib import OAuth1


base = 'Why does @realDonaldTrump '
patterns = [
    base + '{verb1} like a {noun1} that just learned to {verb2}?',
    base + '{verb1} when he could {verb2}?',
    base + 'want to take {noun1} away from {noun2}?',
    base + 'think {noun1} should {verb2}?',
    base + 'put {noun} on his {noun} when he eats it?'
]

random_word_url = (
    'https://wordsapiv1.p.mashape.com/words/?random=true'
    '&partOfSpeech={}'
    '&lettersMax=15'
    '&frequencyMin=4'
)

tweeting_url = (
    'https://api.twitter.com/1.1/statuses/update.json?'
    '&display_coordinates=false'
)


def get_verb(session):
    resp = session.get(random_word_url.format('verb'))
    resp.raise_for_status()
    return resp.json()['word']


def get_noun(session):
    resp = session.get(random_word_url.format('noun'))
    resp.raise_for_status()
    return resp.json()['word']


def make_tweet(session):
    sentence_params = {
        'noun1': get_noun(session),
        'noun2': get_noun(session),
        'verb1': get_verb(session),
        'verb2': get_verb(session)
    }

    return random.choice(patterns).format(**sentence_params)


def send_tweet(status, session, auth):
    url = tweeting_url.format(status)
    resp = session.post(url, data={'status': status}, auth=auth)
    resp.raise_for_status()


def handle(event, context):
    words_session = Session()
    words_session.headers.update(
        {'X-Mashape-Key': os.getenv('WORDS_API_TOKEN'),
        'Accept': 'application/json'}
    )
    tweet = make_tweet(words_session)
    words_session.close()

    twitter_session = Session()
    auth = OAuth1(
        os.getenv('TWITTER_CONSUMER_KEY'),
        os.getenv('TWITTER_CONSUMER_SECRET'),
        os.getenv('TWITTER_ACCESS_TOKEN_KEY'),
        os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    )

    send_tweet(tweet, twitter_session, auth)
