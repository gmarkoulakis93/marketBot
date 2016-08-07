from flask import Flask, request
import json
import requests
from csvRead import findCity, findStreet, findPostal, findFName, findLName, findCardShort
from stripPunct import noPunct
from createOrder import forReceipt
import datetime
import csv

app = Flask(__name__)

#rename variables (don't use something like myDicts)

# This is the page access token needed to talk to the Messenger API
PAT            = 'EAAZAwMVNt37kBAMcdxj0eCz4lcT0s08mShKBE3O9JzwTgLHsCgFM5pj9bZBKnq5T32wVjqZApG6bKOFujVdZAr2DX31SXTKqZC2ZCZAf8NBOHGqrtGwpGZB9sOWjar6n3XifD6G7ywuMrMNbH75dGpw9oYadgdtqVPCrhIU29p2pzwZDZD'

#All the items that the user could order
menu_items     = ["bread", "beer", "milk", "cheese", "steak"]
raw_time_today = datetime.datetime.now()
today          = "%s/%s/%s" % (raw_time_today.month, raw_time_today.day, raw_time_today.year)
tomorrow       = "%s/%s/%s" % (raw_time_today.month, raw_time_today.day + 1, raw_time_today.year)


#These dictionaries are used to populate the API requirements for the receipt template
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
    "bread":"text",
  }.get(food, "Bla")

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
  }.get(food, "N/A")

#function that enables access to the Messenger API
@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

#function that posts to FB server
#we also route what type of message we send depending on what the payload is
@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    cleanDateObject = ''
    if "I want" in message:
      print ("Receipt should send")
      message.replace("one","1")
      message.replace("a","1")
      #message.split(' ')
      order    = []
      myList   = message.split(' ')
      n        = 2
      tuplesL  = [myList[i:i+n] for i in range(len(myList)-n+1)]
      noPunct(tuplesL)
      forReceipt(tuplesL, menu_items, order)
      itemInfoDicts=[]
      for pair in order:
        itemInfoDicts.append({"title": titleDict(pair[1]),"subtitle":subtitle(pair[1]), "quantity":pair[0],"price":pricing(pair[1]),"currency":"USD","image_url":pic(pair[1])})
      pre_receipt(PAT, sender, message)
      send_receipt(PAT, sender, message, itemInfoDicts)
      post_receipt(PAT, sender, message)
    elif "Delivery date" in message:
      delimitMessage = message.split(" ")
      attemptedDate  = delimitMessage[-1].strip()
      try:
        deliveryDateObject = datetime.datetime.strptime(attemptedDate, "%m/%d")
        cleanDateObject    = deliveryDateObject.strftime("%m-%d")
        date_confirm(PAT, sender, message, cleanDateObject)
      except Exception:
        bad_date(PAT, sender, message)
    elif "That date looks great" in message:
      available_time_windows(PAT, sender, message, cleanDateObject)
    else:
      send_message(PAT, sender, message)
  return "ok"

#For our send_message function, this is our rules set
def messageDict(stuff):
  return {
    "Hi":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Hi!":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Hey":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Hey!":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Sup":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Sup!":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "What's up?":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Y":"Great! Check out all the products we offer here (hyperlink or button?). If you know what you want, place your order saying 'I want...'",
    "Sup?":"I'm well. How are you?",
    "Looks good":"What day is best for delivery? Send me the date like this: 'Delivery date: [date in m/dd format]' (remember that the soonest we can deliver is %s)" % tomorrow,
    "Avy":"https://media.licdn.com/mpr/mpr/shrinknp_200_200/p/7/005/085/231/20d3c36.jpg",
  }.get(stuff, "Is this what you'd like? If so, enter 'Y'")

#Now, break down the message payload and extract message and ID
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

#play around with the send_image functionality...not used
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

#main engine for text conversation
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

def pre_receipt(token, recipient, text):
  """Send the message right before receipt template
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": "Great choices. Can you review this receipt and ensure it's what you asked for and also check if the address is right"}
}),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

# def post_receipt(token, recipient, text):
#   """Send the ask for confirmation
#   """

#   r = requests.post("https://graph.facebook.com/v2.6/me/messages",
#     params={"access_token": token},
#     data=json.dumps({
#       "recipient": {"id": recipient},
#       "message": {"text": "How about you give me a 'Looks good' if this is right?"}
# }),

#     headers={'Content-type': 'application/json'})
#   if r.status_code != requests.codes.ok:
#    print r.text

def post_receipt(token, recipient, text):
  """Send the ask for confirmation
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message":{
        "text":"Does this receipt look good?",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"Yes",
            "payload":"receipt_good"
          },
          {
            "content_type":"text",
            "title":"No",
            "payload":"receipt_bad"
          }
        ]
      }
    }

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def date_confirm(token, recipient, text, date):
  """Send the ask for confirmation
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": "So delivery on %s? Reply with 'That date looks great' if it's right." % date}
}),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def bad_date(token, recipient, text):
  """Send the ask for confirmation
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": "That date doesn't seem to be valid. Try again? Remember to use 'Delivery date: [m/dd]' format!"}
}),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def available_time_windows(token, recipient, text, date):
  """Send the ask for confirmation
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": "Awesome. Here are the available time windows on %s" % date}
}),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

#our receipt function that takes the itemInfoDicts created above to extract all the data we need
#as you can see, the majority of the JSON elements are variable -- varies with user and input message
def send_receipt(token, recipient, text, itemInfoDicts):
  """Send the message text to recipient with id recipient.
  """
  TAX_RATE   = .05
  userCity   = findCity(recipient)
  userStreet = findStreet(recipient)
  userPostal = findPostal(recipient)
  userFName  = findFName(recipient)
  userLName  = findLName(recipient)
  userCard   = findCardShort(recipient)
  recip_name = userFName + ' ' + userLName
  prices     = {}
  for d in itemInfoDicts:
    prices[d['title']] = d['price']
  quantities = {}
  for d in itemInfoDicts:
    quantities[d['title']] = d['quantity']
  cost       = sum(prices[k]*int(quantities[k]) for k in prices)
  tax        = TAX_RATE * cost
  total      = cost + tax

  in_data={
    "message": {
      "attachment": {
        "type": "template", 
        "payload": {
          "elements": itemInfoDicts, 
          "payment_method": userCard,
          "timestamp": "1428444852", 
          "adjustments": [
            {
              "amount": 1, 
              "name": "not in calculation"
            }, 
            {
              "amount": 1, 
              "name": "not in calculation"
            }
          ], 
          "recipient_name": recip_name, 
          "currency": "USD", 
          "address": {
            "city": userCity, 
            "country": "US", 
            "state": "CA", 
            "postal_code": userPostal, 
            "street_1": userStreet, 
            "street_2": ""
          }, 
          "order_url": "http://petersapparel.parseapp.com/order?order_id=123456", 
          "summary": {
            "total_cost": total, 
            "total_tax": tax, 
            "subtotal": cost, 
            "shipping_cost": 0
          }, 
          "template_type": "receipt", 
          "order_number": "12345678902"
        }
      }
    }, 
    "recipient": {
      "id": recipient
    }
  }
  
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    json=in_data)

  if r.status_code != requests.codes.ok:
    print r.text

if __name__ == '__main__':
  app.run()