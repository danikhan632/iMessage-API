import time, csv, re, json, threading,os
from datetime import datetime
from flask import Flask, request, jsonify
from imessage_reader import fetch_data
import subprocess
from functools import wraps

app = Flask(__name__)
PASSWORD = os.environ.get('PASSWORD')
MY_NAME=os.environ.get('YOUR_NAME')
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('api_key') != PASSWORD:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


global messages

def update_fd():
    global messages
    while True:
        messages = sorted(fetch_data.FetchData().get_messages(), key=sort_key, reverse=True)
        time.sleep(5)
threading.Thread(target=update_fd).start()


contacts = json.load(open("contacts.json", "r"))
reversed_contacts = {value: key for key, value in contacts.items()}

def getName(phone_number):
    try:
        if "@" in phone_number:
            return phone_number
        elif phone_number.startswith("+"):
            return contacts[phone_number]
        elif len(phone_number) == 10:
            return contacts["1" + phone_number]
        else:
            return contacts["+1" + phone_number]
    except KeyError:
        return phone_number


def sort_key(item):
    return datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S')

def send(phone_number, message):
    applescript = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    try:
        subprocess.run(['osascript', '-e', applescript])
    except Exception as e:
        print(f"Error sending message to {phone_number}: {e}")


@app.route('/send', methods=['POST'])
@require_api_key
def send_message():
    global messages
    try:
        isName = request.args.get('name', True) in ['True', 'true']
        data = request.get_json()
        if 'recipient' not in data or 'message' not in data:
            return jsonify({'error': 'Missing recipient or message in the request'}), 400

        recipient = data['recipient']
        message = data['message']
        if isName:
            recipient =getName(data['recipient'])
        send(recipient, message)
        return jsonify({'status': "ok"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    
@app.route('/messages', methods=['GET'])
@require_api_key
def get_messages():
    global messages
    try:
        num_messages = int(request.args.get('num_messages', 10))
        sent = request.args.get('sent', True) in ['True', 'true']
        formatted = request.args.get('formatted', True) in ['True', 'true']
        if num_messages > len(messages):
            num_messages= len(messages)
        if formatted ==False:
            return jsonify({'messages':messages[:num_messages] }), 200
        temp_messages = []
        # else
        for i in range(0,num_messages):
            sent_by_me=bool(int(messages[i][5]))
            name=getName(messages[i][0])
            timestamp = datetime.strptime(messages[i][2], "%Y-%m-%d %H:%M:%S")
            if sent_by_me==False:
                temp_messages.append({"from":name,"body":messages[i][1],"to":MY_NAME,"datetime":timestamp})
            elif sent_by_me==True and sent==True:
                temp_messages.append({"from":MY_NAME,"body":messages[i][1],"to":name,"datetime":timestamp})
        
        return jsonify({'messages':temp_messages }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def root():
    print(request)
    return jsonify({'messages': "root"}), 200

@app.route('/messages/<person>', methods=['GET'])
@require_api_key
def get_person_messages(person):
    try:
        isName = request.args.get('name', True) in ['True', 'true']
        
        num_messages = int(request.args.get('num_messages', 10))
        sent = request.args.get('sent', True) in ['True', 'true']
        formatted = request.args.get('formatted', True) in ['True', 'true']
        if num_messages > len(messages):
            num_messages= len(messages)
        temp_messages = []
        if formatted ==False:
            for i in range(0,num_messages):
                if messages[i][0] == person:
                    temp_messages.append(messages[i])
            return jsonify({'messages':messages[:num_messages] }), 200
        
        # else
        for i in range(0,num_messages):
            sent_by_me=bool(int(messages[i][5]))
            name=messages[i][0]
            if isName:
                name=getName(messages[i][0])
            timestamp = datetime.strptime(messages[i][2], "%Y-%m-%d %H:%M:%S")
            if name == person:
                if sent_by_me==False:
                    temp_messages.append({"from":name,"body":messages[i][1],"to":MY_NAME,"datetime":timestamp})
                elif sent_by_me==True and sent==True:
                    temp_messages.append({"from":MY_NAME,"body":messages[i][1],"to":name,"datetime":timestamp})
        
        return jsonify({'messages':temp_messages }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recent_contacts', methods=['GET'])
@require_api_key
def get_most_recent_contacts():
    try:
        num_contacts = int(request.args.get('num_contacts', 10))
        recent_contacts = set()
        for message in messages:
            if len(recent_contacts) >= num_contacts:
                break
            if bool(int(message[5])):  # Sent by me
                recent_contacts.add(getName(message[0]))

        return jsonify({'recent_contacts': list(recent_contacts)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT_NUMBER', '5000')))
