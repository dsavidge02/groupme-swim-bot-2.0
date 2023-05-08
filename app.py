from datetime import datetime, timedelta
import csv
from csv import DictWriter
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
    checking = False
    reading = True
    name = data['name']
    txt = data['text'].lower()
    if name == 'MikeGPT':
        return "ok", 200
    if 'palmer' in data['name'].lower() and checking:
        msg = 'I will break into your house and live inside your walls'
        send_message(msg, data['id'])
    if is_question(txt) == 1 and not anti_spam():
    	questionNum = question_handler(txt)
    	if questionNum == 1:
    		msg = shirt_question(txt)
    		send_message(msg, data['id'])
    	elif questionNum == 2:
    		event_question(txt)
    elif reading:
    	send_reminder('reading for question')
    	read_event(name,txt)

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
    url = 'https://api.groupme.com/v3/bots/post'
    info = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg
    }
    print(info)
    requests.post(url, data=json.dumps(info))

def read_lift_days():
	file = open('liftdays.txt')
	lines = file.readlines()
	lift_days = [-1]*3
	for i in range(0,3):
		lift_days[i] = int(lines[i].strip())
	file.close()
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
	if 'events' in txt or 'event' in txt or 'meeting' in txt or 'meetings' in txt:
		return 2
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
		return 'You should be wearing a black shirt!'
	elif day == lift_days[1]:
		return 'You should be wearing a gray shirt!'
	elif day == lift_days[2]:
		return 'You should be wearing a red shirt!'
	else:
		return 'I have not been taught what shirt you wear on ' + dow

def event_question(txt):
	eventFound = 0
	if 'week' in txt:
		eventFound = find_events(7)
	else:
		days = get_days()
		days.append('today')
		days.append('tomorrow')
		for day in days:
			if day in txt:
				eventFound = find_daily_event(day)
	if eventFound == 0:
		msg = 'There doesn\'t seem to be any events'
		send_reminder(msg)
		#print(msg)

#dayRange is how many days in the future would you like to send the reminder about
def find_events(dayRange):
	eventFound = 0
	with open('team_events.csv') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			dt = datetime.strptime(row["dt"], '%Y-%m-%d %H:%M:%S')
			if dt <= datetime.now()+timedelta(hours=(24*dayRange)):
				dateString1 = dt.strftime("%m/%d")
				dateString = ' ('+dateString1+') at ' + dt.strftime("%I:%M %p")
				if(dayRange == 1):
					dateString = ' tomorrow' + dateString
				if(dayRange == 7):
					dow = dt.strftime('%A')
					dateString = ' ' + dow + dateString
				outfitString = ''
				if row["outfit"] != '':
					outfitString = ' and you should wear a ' + row["outfit"]
				msg = 'We have a ' + row["event"] + dateString + ' in ' + row["location"] + outfitString
				send_reminder(msg)
				#print(msg)
				eventFound = 1
	csv_file.close()
	return eventFound

def find_daily_event(day_of_week):
	eventFound = 0
	days = get_days()
	dow1 = day_of_week
	if day_of_week == 'today':
		dow1 = days[datetime.today().weekday()]
	elif day_of_week == 'tomorrow':
		ind = datetime.today().weekday()+1
		if ind > 6:
			ind = 0
		dow1 = days[ind]
	with open('team_events.csv') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			dt = datetime.strptime(row["dt"], '%Y-%m-%d %H:%M:%S')
			dow = dt.strftime('%A').lower()
			if dow == dow1 and dt <= datetime.now()+timedelta(hours=(24*6)):
				dateString1 = dt.strftime("%m/%d")
				dateString = ' ('+dateString1+') at ' + dt.strftime("%I:%M %p")
				outfitString = ''
				if row["outfit"] != '':
					outfitString = ' and you should wear a ' + row["outfit"]
				msg = 'We have a ' + row["event"] + ' ' + day_of_week + dateString + ' in ' + row["location"] + outfitString
				send_reminder(msg)
				#print(msg)
				eventFound = 1
	return eventFound

def clear_events():
	lines = list()
	with open('team_events.csv', 'r') as readFile:
		reader = csv.reader(readFile)
		line_count = 0
		for row in reader:
			if line_count!= 0:
				dt = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
				if datetime.now()<dt:
					lines.append(row)
			line_count += 1
	readFile.close()
	field_names = ['dt', 'location', 'event', 'outfit']
	with open('team_events.csv', 'w') as writeFile:
		writer = csv.writer(writeFile)
		writer.writerow(field_names)
		writer.writerows(lines) 

def get_event_people():
	file = open('event_people.txt')
	lines = file.readlines()
	event_people = ['SOME RANDOM PERSON']*6
	for i in range(0,6):
		event_people[i] = lines[i].strip()
	file.close()
	return event_people

def read_event(name, txt):
	if name in get_event_people():
		send_reminder('Dan is in event people')
		acceptable_events = ['meeting', 'event', 'activity']
		event = 'NO EVENT'
		for item in acceptable_events:
			if item.lower() in txt.lower():
				event  = item
				send_reminder(event)
				break
		acceptable_locations = ['Mueller', 'Harkness', 'Pool', 'Team Room', 'ECAV', 'Hall of Fame', 'TBD']
		location = 'NO LOCATION'
		for item in acceptable_locations:
			if item.lower() in txt.lower():
				location = item
				send_reminder(location)
				break
		acceptable_outfits = [' black ', 'gray ', ' grey ', ' red ', ' warmups ', ' quarterzip ', ' RPI Swim Gear ', ' RPI gear ', ' black.', 'gray.', ' grey.', ' red.', ' warmups.', ' quarterzip.', ' RPI Swim Gear.', ' RPI gear.']
		outfit = ''
		for item in acceptable_outfits:
			if item.lower() in txt.lower():
				outfit = item
				break
		dt = find_datetime(txt)
		send_reminder(datetime.strftime(dt, '%Y-%m-%d %H:%M:%S'))
		if event != 'NO EVENT' and location != 'NO LOCATION' and dt != -1:
			send_reminder('event created')
			create_event(dt, location, event, outfit)

def find_datetime(txt):
	date = find_date(txt)
	adder = 0
	if date == '':
		temp = make_date(txt)
		date = temp[0]
		adder = temp[1]
	temp2 = find_time(txt)
	time = temp2[0]
	adder2 = temp2[1]
	if date != '' and time != '':
		dt = datetime.strptime((date + ' ' + time), '%Y-%m-%d %H:%M:%S')
		dt = dt + timedelta(days = adder) + timedelta(hours = adder2)
		return dt
	else:
		return -1

def make_date(txt):
	date = datetime.now().strftime('%Y-%m-%d')
	days = get_days()
	day = -1
	adder = 0
	if 'today' in txt:
		return [date,adder]
	if 'tomorrow' in txt:
		adder = 1
		return [date,adder]
	for i in range(0,len(days)):
		if days[i] in txt:
			possible_next = 'next ' + days[i]
			if possible_next in txt:
				adder = 7
			day = i
			curr = datetime.today().weekday()
			if curr > day:
				adder = adder + curr - day
			else:
				adder = adder + day - curr
			return [date, adder]

def find_date(txt):
	i = txt.find('/')
	date = ''
	if i != -1:
		i = txt.index('/')
	else:
		return date
	while i != -1:
		if txt[i-2].isnumeric():
			date = date+txt[i-2]
		else:
			date = date + '0'
		if txt[i-1].isnumeric():
			date = date+txt[i-1]
		date = date + '-'
		if txt[i+1].isnumeric():
			if not txt[i+2].isnumeric():
				date = date + '0'
			date = date+txt[i+1]
			if txt[i+2].isnumeric():
				date = date+txt[i+2]
		if len(date) != 5:
			date = ''
			j = txt.find('/', i+1)
			if j !=-1:
				i = txt.index('/', i+1)
			else:
				return date
		else:
			i=-1
	date = datetime.now().strftime('%Y') + '-' + date
	return date

def find_time(txt):
	adder = 0
	if 'pm' in txt.lower():
		adder = 12
	i = txt.find(':')
	time = ''
	if i != -1:
		i = txt.index(':')
	else:
		return time
	while i != -1:
		if txt[i-2].isnumeric():
			time = time+txt[i-2]
		else:
			time = time + '0'
		if txt[i-1].isnumeric():
			time = time+txt[i-1]
		time = time + ':'
		if txt[i+1].isnumeric():
			time = time+txt[i+1]
		if txt[i+2].isnumeric():
			time = time+txt[i+2]
		if len(time) != 5:
			time = ''
			j = txt.find(':', i+1)
			if j != -1:
				i = txt.index(':', i+1)
			else:
				return [time,adder]
		else:
			i=-1
	time = time + ':00'
	return [time,adder]


def create_event(dt, location, event, outfit):
	if(dt < datetime.now()):
		return 0
	with open('team_events.csv') as csv_file:
		csv_reader = csv.DictReader(csv_file)
		for row in csv_reader:
			dt2 = datetime.strptime(row["dt"], '%Y-%m-%d %H:%M:%S')
			if(dt2 == dt):
				return 0
	csv_file.close()
	field_names = ['dt', 'location', 'event', 'outfit']
	dict = {'dt': dt, 'location': location, 'event': event, 'outfit':outfit}
	with open('team_events.csv', mode='a') as team_events:
		event_writer = DictWriter(team_events, fieldnames = field_names)
		event_writer.writerow(dict)

def anti_spam():
	spam_detected = False
	file = open('anti_spam.txt')
	lines = file.readlines()
	last_ping = datetime.strptime(lines[0].strip(), '%Y-%m-%d %H:%M:%S')
	count_pings = int(lines[1].strip())+1
	if count_pings >= 4 and datetime.now() - timedelta(seconds=30) < last_ping:
		spam_detected = True
	elif count_pings >= 4:
		count_pings = 1
	file.close()
	with open('anti_spam.txt', 'w') as file:
		file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n' + str(count_pings) + '\n')
	return spam_detected

def main():
	clear_events()
	if datetime.today().weekday() == 6:
		send_reminder('WEEKLY REMINDERS:')
		find_events(7)
	else:
		send_reminder('DAILY REMINDERS:')
		find_events(1)

if __name__ == "__main__":
    main()
