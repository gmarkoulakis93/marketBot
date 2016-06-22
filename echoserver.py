from flask import Flask, request
import json
import requests

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAZAwMVNt37kBAMcdxj0eCz4lcT0s08mShKBE3O9JzwTgLHsCgFM5pj9bZBKnq5T32wVjqZApG6bKOFujVdZAr2DX31SXTKqZC2ZCZAf8NBOHGqrtGwpGZB9sOWjar6n3XifD6G7ywuMrMNbH75dGpw9oYadgdtqVPCrhIU29p2pzwZDZD'

@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    #if message == "Avy":
    #  send_image(PAT, sender, message)
    #else:
    send_message(PAT, sender, message)
  return "ok"

def messageDict(stuff):
  #defines what responses we will give to different text inputs
  return {
    "Sup":"I'm well. How are you?",
    "Sup?":"I'm well. How are you?",
    "3 loaves of bread, a 6 pack of beer, and ground beef":"Sounds great, please review this receipt. Say 'OK' if this is the correct order",
    "Avy":"https://media.licdn.com/mpr/mpr/shrinknp_200_200/p/7/005/085/231/20d3c36.jpg",
  }.get(stuff, "I'm sorry, I didn't understand")

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"
  #for event in messaging_events:
  #  if "message" in event and "text" in event["message"]:
  #    yield event["sender"]["id"], messageDict(event["message"]["text"]).encode('unicode_escape')
    #elif "message" in event and "attachment" in event["message"]:
    #  yield event["sender"]["id"], event["url"]:"https://media.licdn.com/mpr/mpr/shrinknp_200_200/p/7/005/085/231/20d3c36.jpg"
      #if event["message"]["text"] == "Sup":
        #yield event["sender"]["id"], event["type"]:"image" and event["url"]:"https://media.licdn.com/mpr/mpr/shrinknp_200_200/p/7/005/085/231/20d3c36.jpg"
       # yield event["sender"]["id"], "Figure out images later".encode('unicode_escape')
      #else:
      #yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
       # yield event["sender"]["id"], "Argh".encode('unicode_escape')
#    else:
#      yield event["sender"]["id"], "I can't echo this"

def send_image(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {
        "attachment": {
          "type":"image",
          "payload":{
            text
          }
        }
      }
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient":{
        "id":recipient
      },
      "message":{
        "attachment":{
          "type":"image",
          "payload":{
            "url":"https://media.licdn.com/mpr/mpr/shrinknp_200_200/p/7/005/085/231/20d3c36.jpg"
      }
    }
  }
}),
#      "recipient": {"id": recipient},
#      "message": {"text": text.decode('unicode_escape')}
#    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

if __name__ == '__main__':
  app.run()