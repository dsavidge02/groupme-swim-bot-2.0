import os
import json
import random

import requests

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)
    # We don't want to reply to ourselves!
    if random.random() < .05:
        msg = 'Dislike Button'
        send_message(msg, data['id'])
    elif 'anthony' in data['name'].lower() and random.random() < .5:
        msg = 'When did I ask?'
        send_message(msg, data['id'])

    return "ok", 200

@app.route('/', methods=['GET'])
def ping():
    return "ok", 200

def send_message(msg, reply_id):
    url  = 'https://api.groupme.com/v3/bots/post'

    info = {
          'bot_id' : os.getenv('GROUPME_BOT_ID'),
          'text'   : msg,
          'attachments':
          [{
            'type': 'reply',
            'reply_id': reply_id,
            'base_reply_id': reply_id
          }]
         }

    print(info)

    requests.post(url, data=json.dumps(info))
