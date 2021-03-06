import hashlib
import hmac
import os
import urllib

import postmark
import requests
from postmark_inbound import PostmarkInbound
from raven.contrib.flask import Sentry

from flask import Flask, request, render_template, redirect


#
# app configuration
#

SERVICE_EMAIL = os.environ.get('SERVICE_EMAIL')

POSTMARK_KEY = os.environ.get('POSTMARK_KEY')
POSTMARK_SENDER = os.environ.get('POSTMARK_SENDER')

SUNLIGHT_KEY = os.environ.get('SUNLIGHT_KEY')
SUNLIGHT_SECRET = os.environ.get('SUNLIGHT_SECRET')
SUNLIGHT_URL = os.environ.get('SUNLIGHT_URL')

SENTRY_DSN = os.environ.get('SENTRY_DSN')

REGISTRATION_ENABLED = os.environ.get('REGISTRATION_ENABLED', '') != ''

ENABLED_HASHES = os.environ.get('ENABLED_HASHES', '').split(',')

#
# API registration
#

def get_signature(params):
    data = sorted([(k, unicode(v).encode('utf-8')) for k, v in params.items() if k != 'signature'])
    qs = urllib.urlencode(data)
    return hmac.new(SUNLIGHT_SECRET, qs, hashlib.sha1).hexdigest()


def key_notification(key, addr):
    context = {
        'key': key,
        'email': addr,
    }
    message = render_template('email/success.txt', **context)
    mail = postmark.PMMail(
        api_key=POSTMARK_KEY,
        sender=POSTMARK_SENDER,
        to=addr,
        subject='Here is your brand new Sunlight API key!',
        text_body=message,
    )
    mail.send()


def disabled_notification(addr):
    message = render_template('email/disabled.txt')
    mail = postmark.PMMail(
        api_key=POSTMARK_KEY,
        sender=POSTMARK_SENDER,
        to=addr,
        subject='Ack! A small problem with your Sunlight Foundation API key',
        text_body=message,
    )
    mail.send()


def register_key(addr, name):
    params = {
        'apikey': SUNLIGHT_KEY,
        'email': addr,
        'name': name or 'Sunlight Event Attendee',
    }
    params['signature'] = get_signature(params)
    resp = requests.post(SUNLIGHT_URL, params)
    data = resp.json()
    return data.get('key')


#
# init web app
#

app = Flask(__name__)

if SENTRY_DSN:
    app.config['SENTRY_DSN'] = SENTRY_DSN
    sentry = Sentry(app)


#
# routes
#

@app.route('/email', methods=['POST'])
def email_handler():

    email = PostmarkInbound(json=request.data)

    app.logger.debug('recipient addr = %s' % email.to())
    app.logger.debug('sender addr = %s' % email.sender())

    valid_recipients = [e for e in email.to() if e.get('Email').startswith(SERVICE_EMAIL)]

    if valid_recipients:

        sender = email.sender()

        addr = sender.get('Email')
        name = sender.get('Name')

        if REGISTRATION_ENABLED and email.mailbox_hash() in ENABLED_HASHES:

            key = register_key(addr, name)

            if key:
                key_notification(key, addr)
                app.logger.debug('key = %s' % key)
            else:
                disabled_notification(addr)

        else:
            disabled_notification(addr)

    return ''


@app.route('/email', methods=['GET'])
def mailto_redirect():

    subject = "Hello API"
    body = "Just hit Send and you'll receive an email containing your new API key. You'll also be agreeing to our terms of service, which you can read at http://sunlightfoundation.com/api/usage/terms."

    return redirect('mailto:%s?subject=%s&body=%s' % (SERVICE_EMAIL, subject, body))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
