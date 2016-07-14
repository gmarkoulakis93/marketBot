from flask import Flask, request
import json
import requests
from csvRead import findAddress
from stripPunct import noPunct
from createOrder import forReceipt
import csv
#ugh
app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAZAwMVNt37kBAMcdxj0eCz4lcT0s08mShKBE3O9JzwTgLHsCgFM5pj9bZBKnq5T32wVjqZApG6bKOFujVdZAr2DX31SXTKqZC2ZCZAf8NBOHGqrtGwpGZB9sOWjar6n3XifD6G7ywuMrMNbH75dGpw9oYadgdtqVPCrhIU29p2pzwZDZD'

menu_items = ["bread", "beer", "milk", "cheese", "steak"]

myDict = {}

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
      if "I want" in message:
        message.replace("one","1")
        #message.replace("a","1")
        #message.split(' ')
        order = []
        myList   = message.split(' ')
        n = 2
        tuplesL  = [myList[i:i+n] for i in range(len(myList)-n+1)]
        noPunct(tuplesL)
        forReceipt(tuplesL, menu_items, order)
        for pair in tuplesL:
          global myDict
          myDict = {"title": titleDict(pair[1]),"subtitle":subtitle(pair[1]), "quantity":pair[0],"price":pricing(pair[1]),"currency":"USD","image_url":pic(pair[1])}
        send_receipt(PAT, sender, message)
        send_message(PAT, sender, message)
      else:
        send_message(PAT, sender, message)
  return "ok"

def titleDict(food):
  return {
    "milk":"Clover Milk Non-Fat",
    "bread":"Semi-Freddis Ciabatta",
    "beer":"6-pack of Ballast Point",
    "cheese":"Tillamook Cheddar",
  }.get(food,"Hmm, not sure what happened. Try again?")

def subtitle(food):
  return {
    "milk":"One Gallon",
    "beer":"Rated number one on Beer Advocate",
    "bread":" ",
  }.get(food, " ")

def pricing(food):
  return {
    "milk":6,
    "bread":10,
    "beer":13,
    "cheese":4,
  }.get(food, "We'll need to check on that")

def pic(food):
  return {
    "milk":"http://www.clover.co.za/zpimages/thumb/450/550/data/products/milk_2_fresh_2l.png",
    "bread":"http://www.hungryhungryhippie.com/wp-content/uploads/2012/01/IMG_5171.jpg",
    "beer":"http://www.southernspirits.com/wp-content/uploads/2016/02/ballast-point.jpg",
  }.get(food, " ")

def messageDict(stuff):
  #defines what responses we will give to different text inputs
  return {
    "Sup":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order?",
    "y":"Great. What would you like?",
    "Sup?":"I'm well. How are you?",
    "3 loaves of bread, a 6 pack of beer, and ground beef":"Sounds great, please review this receipt. Say 'OK' if this is the correct order",
    "Avy":"https://media.licdn.com/mpr/mpr/shrinknp_200_200/p/7/005/085/231/20d3c36.jpg",
  }.get(stuff, "Is this what you'd like? If so, enter 'Y'")

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
  in_data=json.loads('{"recipient":{"id":"recipient"},"message":{"attachment":{"type":"template","payload":{"template_type":"receipt","recipient_name":"Stephane Crozatier","order_number":"12345678902","currency":"USD","payment_method":"Visa 2345",        "order_url":"http://petersapparel.parseapp.com/order?order_id=123456","timestamp":"1428444852", "elements":[],"address":{"street_1":"1 Hacker Way","street_2":"","city":"San Francisco","postal_code":"94025","state":"CA","country":"US"},"summary":{"subtotal":75.00,"shipping_cost":4.95,"total_tax":6.19,"total_cost":56.14},"adjustments":[{"name":"New Customer Discount","amount":20},{"name":"$10 Off Coupon","amount":10}]}}}}')
  #in_data['message']['attachment']['payload']["elements"][0]["quantity"]=q
  in_data["recipient"]["id"]=recipient
  userAddress=findAddress(recipient)
  in_data['message']['attachment']['payload']['address']['city']=userAddress
  in_data['message']['attachment']['payload']['elements'].append(myDict)
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps(in_data),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

if __name__ == '__main__':
  app.run()