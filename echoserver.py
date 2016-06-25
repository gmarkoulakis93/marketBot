from flask import Flask, request
import json
import requests

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAZAwMVNt37kBAMcdxj0eCz4lcT0s08mShKBE3O9JzwTgLHsCgFM5pj9bZBKnq5T32wVjqZApG6bKOFujVdZAr2DX31SXTKqZC2ZCZAf8NBOHGqrtGwpGZB9sOWjar6n3XifD6G7ywuMrMNbH75dGpw9oYadgdtqVPCrhIU29p2pzwZDZD'
q=0

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
    if message == "Receipt":
      send_receipt(PAT, sender, message)
    else:
      if "milk" in message:
        #message.split(' ')
        place = message.index("milk")-2
        global q
        q = message[place]
        send_receipt(PAT, sender, message)
      else:
        send_message(PAT, sender, message)
  return "ok"

def messageDict(stuff):
  #defines what responses we will give to different text inputs
  return {
    "Sup":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order?",
    "y":"Great. What would you like?",
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
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": messageDict(text.decode('unicode_escape'))}
}),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text
def send_receipt(token, recipient, text):
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
            "type":"template",
            "payload":{
              "template_type":"receipt",
              "recipient_name":"Stephane Crozatier",
              "order_number":"12345678902",
              "currency":"USD",
              "payment_method":"Visa 2345",        
              "order_url":"http://petersapparel.parseapp.com/order?order_id=123456",
              "timestamp":"1428444852", 
              "elements":[
                {
                  "title":"Classic White T-Shirt",
                  "subtitle":"100% Soft and Luxurious Cotton",
                  "quantity":2,
                  "price":50,
                  "currency":"USD",
                  "image_url":"http://petersapparel.parseapp.com/img/whiteshirt.png"
                },
                {
                  "title":"Clover Milk",
                  "subtitle":"Whole Fat",
                  "quantity":q,
                  "price":2.50,
                  "currency":"USD",
                  "image_url":"http://www.clover.co.za/zpimages/thumb/450/550/data/products/milk_2_fresh_2l.png"
                }
              ],
              "address":{
                "street_1":"1 Hacker Way",
                "street_2":"",
                "city":"Menlo Park",
                "postal_code":"94025",
                "state":"CA",
                "country":"US"
              },
              "summary":{
                "subtotal":75.00,
                "shipping_cost":4.95,
                "total_tax":6.19,
                "total_cost":56.14
              },
              "adjustments":[
                {
                  "name":"New Customer Discount",
                  "amount":20
                },
                {
                  "name":"$10 Off Coupon",
                  "amount":10
                }
          ]
        }
      }
    }
  }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

if __name__ == '__main__':
  app.run()