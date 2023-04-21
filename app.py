import os
import json
import random

import requests

from datetime import datetime

from flask import Flask, request

days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

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
    elif 'palmer' in data['name'].lower() and checking==1:
        msg = 'I will break into your house and live inside your walls'
        send_message(msg, data['id'])
    elif is_question(txt) == 1:
    	msg = check_messages(txt)
    	send_message(msg, data['id'])
    # elif check_messages(txt)==1:
    #     msg = 'I don\'t know the answer to that yet, sorry'
    #     send_message(msg, data['id'])

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
def is_question(txt):
	if '?' in txt or 'what' in txt:
		return 1
	return 0

def check_messages(txt):
	if 'color' in txt or 'shirt' in txt:
		adder = 0
		day = -1
		if 'tomorrow' in txt:
			adder = 1
		for i in range(0,len(days)):
			if days(i) in txt:
				day = days(i)
		return whatShirt(adder,day)
	return 'not sure if I know the answer to this yet, sorry'

def whatShirt(a, d):
	day = d
	if day == -1:
		day = datetime.today().weekday()
	day += adder
	if day > 6:
		day = 0
	dow = days(day)
	if day == 1:
		return 'you should be wearing a black shirt!'
	elif day == 2:
		return 'you should be wearing a gray shirt!'
	elif day == 4:
		return 'you should be wearing a red shirt!'
	else:
		return 'I have not been taught what shirt you wear on ' + dow
