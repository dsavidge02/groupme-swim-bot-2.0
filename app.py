import os
import json
import random

import requests

from datetime import datetime, timedelta
import csv
from csv import DictWriter

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
    elif 'palmer' in data['name'].lower() and checking==1:
        msg = 'I will break into your house and live inside your walls'
        send_message(msg, data['id'])
    elif is_question(txt) == 1:
    	if question_handler(txt) == 1:
    		msg = shirt_question(txt)
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
	
def send_reminder(msg):
	url  = 'https://api.groupme.com/v3/bots/post'
    info = {
          'bot_id' : os.getenv('GROUPME_BOT_ID'),
          'text'   : msg,
         }
    print(info)
    requests.post(url, data=json.dumps(info))
	
def read_lift_days():
	file = open('liftdays.txt')
	lines = file.readlines()
	lift_days = [-1]*3
	for i in range(0,3):
		lift_days[i] = int(lines[i].strip())
	return lift_days

def get_days():
	days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
	return days

def is_question(txt):
	if '?' in txt or 'what' in txt:
		return 1
	return 0

def question_handler(txt):
	if 'color' in txt or 'shirt' in txt: 
		return 1
	return 0

def shirt_question(txt):
	days = get_days()
	adder = 0
	day = -1
	if 'tomorrow' in txt:
		adder = 1
	for i in range(0,len(days)):
		if days[i] in txt:
			day = i
	return whatShirt(adder,day)

def whatShirt(a, d):
	days = get_days()
	day = d
	if day == -1:
		day = datetime.today().weekday()
	day += a
	if day > 6:
		day = 0
	dow = days[day]
	lift_days = read_lift_days()
	if day == lift_days[0]:
		return 'you should be wearing a black shirt!'
	elif day == lift_days[1]:
		return 'you should be wearing a gray shirt!'
	elif day == lift_days[2]:
		return 'you should be wearing a red shirt!'
	else:
		return 'I have not been taught what shirt you wear on ' + dow

def create_event(dt, location, event, outfit):
	field_names = ['dt', 'location', 'event', 'outfit']
	dict = {'dt': dt, 'location': location, 'event': event, 'outfit':outfit}
	with open('team_events.csv', mode='a') as team_events:
		event_writer = DictWriter(team_events, fieldnames = field_names)
		event_writer.writerow(dict)
		team_events.close()
		
def find_events():
	with open('team_events.csv') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			dt = datetime.strptime(row["dt"], '%Y-%m-%d %H:%M:%S')
			if datetime.now()-timedelta(hours=24) <= dt <= datetime.now()+timedelta(hours=24):
				dateString1 = dt.strftime("%m/%d")
				dateString = ' tomorrow ('+dateString1+') at ' + dt.strftime("%I:%M %p")
				outfitString = ''
				if row["outfit"] != '':
					outfitString = ' and you should wear a ' + row["outfit"]
				msg = 'We have a ' + row["event"] + dateString + ' in ' + row["location"] + outfitString
				send_reminder(msg)
	csv_file.close()

def main():
	find_events()

if __name__ == "__main__":
    main()
