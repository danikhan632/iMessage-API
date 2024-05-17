# iMessage API

This is a simple API to interact with iMessages using a Flask server. It allows you to send messages, retrieve messages, and fetch recent contacts.

## Prerequisites

- Python 3.x
- Flask
- Access to an iMessage account
- iMessage reader

## Installation


1. Clone this repository:

```
git clone https://github.com/danikhan632/iMessage-API.git
```

2. Change to the directory:
```
cd iMessage-api
```


3. Install the required packages:
```
pip install -r requirements.txt
```
4. Download contacts from iCloud, click select all then export vCard. Rename output and move to this directory

![alt text](https://i.imgur.com/47trZvZ.png)

5. Enable full disk access on either Terminal or iTerm, whichever one you plan to run the server on.

![alt text](https://i.imgur.com/tRkX16J.png)

6. Now that you have renamed the iCloud contacts file to contacts.vcf run this to turn the contacts to json

```
python3 icloud_parser.py
```

Now rename ".env.template" to ".env"and set a  password, your name, and port number for this to run off. Replace `$user` in `DB_FILEPATH` with your user account name.
```
PASSWORD=password
YOUR_NAME=your-name
PORT_NUMBER=5000
DB_FILEPATH=/Users/$user/Library/Messages/chat.db
```

Now to run to run the api server, run the following command
```
python3 server.py
```


# iMessage API Docs

## Endpoints

### Send a message

**POST** `/send`

Send a message to a recipient.

#### Parameters

- `recipient`: (Required) The phone number or name of the recipient.
- `message`: (Required) The content of the message.
- `name`: (Optional, default is `true`) If `true`, the recipient parameter will be treated as a name. If `false`, the recipient parameter will be treated as a phone number.

#### Example

```bash
curl -X POST "http://localhost:5000/send" \
  -H "api_key: <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"recipient": "John Doe", "message": "Hello!"}'

```


### Get messages
**GET**  /messages

Retrieve a list of messages.

#### Parameters
- 'num_messages': (Optional, default is 10) The number of messages to retrieve.
- 'sent': (Optional, default is true) If true, includes messages sent by you. If false, only includes messages received by you.
- 'formatted': (Optional, default is true) If true, returns messages in a more readable format.
Example
```
curl "http://localhost:5000/messages?num_messages=5&sent=true&formatted=true" \
     -H "api_key: <your-api-key>"
```


### Get most recent contacts
**GET** /recent_contacts

Retrieve a list of your most recent contacts.

#### Parameters
- num_contacts: (Optional, default is 10) The number of recent contacts to retrieve.
Example
```
curl "http://localhost:5000/recent_contacts?num_contacts=5"
```