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
    checking = 0
    txt = data['text'].lower()
    # We don't want to reply to ourselves!
    if data['name'] == 'The Anti Palmer':
        return "ok", 200
    elif 'palmer' in data['name'].lower() and checking=1:
        msg = 'I will break into your house and live inside your walls'
        send_message(msg, data['id'])
    elif check_messages(txt)==1
        msg = 'I don't know the answer to that yet, sorry'
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
    
def check_messages(txt):
	if '?' in txt
		return 1 
