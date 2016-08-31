from flask import Flask, request
import json
import requests
from csvRead import findCity, findStreet, findPostal, findFName, findLName, findCardShort
from stripPunct import noPunct
from createOrder import forReceipt
import datetime
import csv

app = Flask(__name__)



#https://delivery-testing.herokuapp.com/ place in "Callback URL" when not running locally

# This is the page access token needed to talk to the Messenger API
PAT            = 'EAAZAwMVNt37kBAMcdxj0eCz4lcT0s08mShKBE3O9JzwTgLHsCgFM5pj9bZBKnq5T32wVjqZApG6bKOFujVdZAr2DX31SXTKqZC2ZCZAf8NBOHGqrtGwpGZB9sOWjar6n3XifD6G7ywuMrMNbH75dGpw9oYadgdtqVPCrhIU29p2pzwZDZD'

#All the items that the user could order
menu_items     = ["bread", "beer", "milk", "cheese", "steak"]
browse_list    = ["Bread!", "Beer!", "Milk!", "Cheese!", "Steak!"]
take_back_list = []
for stuff in menu_items:
  take_back_list.append("Eh, don't want %s" % stuff)

raw_time_today = datetime.datetime.now()
today          = "%s/%s/%s" % (raw_time_today.month, raw_time_today.day, raw_time_today.year)
tomorrow       = "%s/%s" % (raw_time_today.month, raw_time_today.day + 1)
oneAfter       = "%s/%s" % (raw_time_today.month, raw_time_today.day + 2)
twoAfter       = "%s/%s" % (raw_time_today.month, raw_time_today.day + 3)
threeAfter     = "%s/%s" % (raw_time_today.month, raw_time_today.day + 4)
fourAfter      = "%s/%s" % (raw_time_today.month, raw_time_today.day + 5)
fiveAfter      = "%s/%s" % (raw_time_today.month, raw_time_today.day + 6)
dateList       = [tomorrow, oneAfter, twoAfter, threeAfter, fourAfter, fiveAfter]
timeList       = ["%s Time1: 3-4pm" % tomorrow,"%s Time2: 4-5pm" % tomorrow, "%s Time3: 5-6pm" % tomorrow,
                  "%s Time1: 3-4pm" % oneAfter,"%s Time2: 4-5pm" % oneAfter, "%s Time3: 5-6pm" % oneAfter,
                  "%s Time1: 3-4pm" % twoAfter,"%s Time2: 4-5pm" % twoAfter, "%s Time3: 5-6pm" % twoAfter,
                  "%s Time1: 3-4pm" % threeAfter,"%s Time2: 4-5pm" % threeAfter, "%s Time3: 5-6pm" % threeAfter,
                  "%s Time1: 3-4pm" % fourAfter,"%s Time2: 4-5pm" % fourAfter, "%s Time3: 5-6pm" % fourAfter,
                  "%s Time1: 3-4pm" % fiveAfter,"%s Time2: 4-5pm" % fiveAfter, "%s Time3: 5-6pm" % fiveAfter]

myBasket       = []
#create a dictionary that houses the appropriate data structure
#e.g.,
#foods = {bread: {bread1:{"title":"title1", "price":123},bread2:{"title":"title2", "price":222}}}
#build out the above and implement into JSON, remember, you'll need an extra argument in the carousel 
#function and you'll need to capture the user's message in handle_messages

foods      = {"bread": {
                "bread1.1":{
                  "title"           :"Semi-Freddis Ciabatta",
                  "image_url"       :"http://www.hungryhungryhippie.com/wp-content/uploads/2012/01/IMG_5171.jpg",
                  "subtitle"        :"$5 per loaf",
                  "forPayloadOne"   :"1 bread1.1",
                  "receiptSubtitle" :"Delicious loaf",
                  "receiptPrice"    : 5},
                "bread1.2":{
                  "title"           :"Semi-Freddis Sourdough",
                  "image_url"       :"http://www.seriouseats.com/images/2013/08/20130820-san-francisco-bread-taste-test-17.jpg",
                  "subtitle"        :"$4 per loaf",
                  "forPayloadOne"   :"1 bread1.2",
                  "receiptSubtitle" :"Delicious loaf",
                  "receiptPrice"    : 4},
                "bread1.3":{
                  "title"           :"Semi-Freddis Wheat Roll",
                  "image_url"       :"http://www.semifreddis.com/uploads/media_items/deli-wheat.900.600.s.jpg",
                  "subtitle"        :"$2.50 per loaf",
                  "forPayloadOne"   :"1 bread1.3",
                  "receiptSubtitle" :"Delicious loaf",
                  "receiptPrice"    : 2.5}
                      },
              "milk": {
                "milk1.1":{
                  "title"           :"Clover Fat Free (Gallon)",
                  "image_url"       :"https://www.grubmarket.com/images/large/grubmarketdairy/9419646821_clover_organic_farms_fat_free_milk.jpg",
                  "subtitle"        :"$3",
                  "forPayloadOne"   :"1 milk1.1",
                  "receiptSubtitle" :"Delicious milk",
                  "receiptPrice"    : 3},
                "milk1.2":{
                  "title"           :"Clover Chocolate Milk",
                  "image_url"       :"https://s3.amazonaws.com/static.caloriecount.about.com/images/medium/clover-stornetta-farms-percent-172233.jpg",
                  "subtitle"        :"$2",
                  "forPayloadOne"   :"1 milk1.2",
                  "receiptSubtitle" :"Delicious milk",
                  "receiptPrice"    : 2},
                "milk1.3":{
                  "title"           :"Clover Whole Milk",
                  "image_url"       :"https://s3.amazonaws.com/static.caloriecount.about.com/images/medium/clover-organic-farms-milk-80300.jpg",
                  "subtitle"        :"$4",
                  "forPayloadOne"   :"1 milk1.3",
                  "receiptSubtitle" :"Delicious milk",
                  "receiptPrice"    : 4}
                }
              }

#create a list to check against for the postback to see when we are receiving a message that should add to the basket
listForPostback = []
for k in foods:
  for x in foods[k]:
    listForPostback.append(x)

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
basket = []
@app.route('/', methods=['POST'])
def handle_messages(basket):
  print "Handling Messages"
  payload = request.get_data()
  print payload
  itemInfoDicts = []
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    cleanDateObject = ''
    deliveryDate    = ''
    deliveryTime    = ''
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
    elif message == "Hi": #expand this to check for a set of greetings
      order_prompt(PAT, sender, message)
    elif message == "Receipt Looks Good":
      potentialDeliveryDates(PAT, sender, message)
    elif message == "Yes, let's order":
      itemInfoDicts = []
      initial_item_prompt(PAT, sender, message)
    elif message == "back2categories":
      initial_item_prompt(PAT, sender, message)
    elif message in browse_list:
      orderedItem = message[:-1].lower()
      browse_set1(PAT, sender, message, orderedItem)
    #elif "Delivery date" in message:
    #  delimitMessage = message.split(" ")
    #  attemptedDate  = delimitMessage[-1].strip()
    #  try:
    #    deliveryDateObject = datetime.datetime.strptime(attemptedDate, "%m/%d")
    #    cleanDateObject    = deliveryDateObject.strftime("%m-%d")
    #    date_confirm(PAT, sender, message, cleanDateObject)
    #  except Exception:
    #    bad_date(PAT, sender, message)
    elif message.split(' ')[1] in listForPostback:
      basketAdd = message.split(' ')
      for k in foods:
        for thing in foods[k]:
          if thing == basketAdd[1]:
            basketAdd.append(k)
      broadCat       = basketAdd[-1]
      quantityChosen = basketAdd[0]
      specificItem   = basketAdd[1]
      receiptTitle   = foods[broadCat][specificItem]["title"]
      receiptSub     = foods[broadCat][specificItem]["receiptSubtitle"]
      thePrice       = foods[broadCat][specificItem]["receiptPrice"]
      picture        = foods[broadCat][specificItem]["image_url"]
      print(basket)
      basket.append({"title": receiptTitle,"subtitle":receiptSub, "quantity":quantityChosen,"price":thePrice,"currency":"USD","image_url":picture})
      print(basket)
      #addToBasket("add", itemInfoDicts, dictToAdd)
      #send_receipt(PAT, sender, message, itemInfoDicts)
      followUp_item_prompt(PAT, sender, message)
    elif message in dateList:
      deliveryDate = message
      print (deliveryDate)
      available_times(PAT, sender, message, deliveryDate)
    #  available_time_windows(PAT, sender, message, cleanDateObject)
    elif message in timeList:
      findTime     = message.split(' ')
      deliveryTime = findTime[-1]
      deliveryDate = findTime[0]
      print (deliveryTime)
      wrapUpMessage2(PAT, sender, message, deliveryDate, deliveryTime)
    else:
      send_message(PAT, sender, message)
  return "ok"

#For our send_message function, this is our rules set
def messageDict(stuff):
  return {
    #"Hi":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Hi!":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Hey":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Hey!":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Sup":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Sup!":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "What's up?":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order? Send me 'Y' if so.",
    "Y":"Great! Check out all the products we offer here (hyperlink or button?). If you know what you want, place your order saying 'I want...'",
    "Sup?":"I'm well. How are you?",
    "Receipt Looks Good":"What day is best for delivery? Send me the date like this: 'Delivery date: [date in m/dd format]' (remember that the soonest we can deliver is %s)" % tomorrow,
    "Thanks":"You betcha",
    "Thanks!":"You betcha",
    "Naw":"Hmmm...I'm sorry, I'm not a very smart bot. I just take orders :("
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
    elif "postback" in event:
      yield event["sender"]["id"], event["postback"]["payload"]
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
  """leverage quick reply buttons to confirm receipt is as desired
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
            "title":"Receipt Looks Good",
            "payload":"receipt_good"
          },
          {
            "content_type":"text",
            "title":"Hmm, not quite",
            "payload":"receipt_bad"
          }
        ]
      }
    }),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def potentialDeliveryDates(token, recipient, text):
  """leverage quick reply buttons to confirm a delivery date
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message":{
        "text":"Which of these dates were you looking to have stuff delivered?",
        "quick_replies":[
          {
            "content_type":"text",
            "title":tomorrow,
            "payload":"today+1"
          },
          {
            "content_type":"text",
            "title":oneAfter,
            "payload":"today+2"
          },
          {
            "content_type":"text",
            "title":twoAfter,
            "payload":"today+3"
          },
          {
            "content_type":"text",
            "title":threeAfter,
            "payload":"today+4"
          },
          {
            "content_type":"text",
            "title":fourAfter,
            "payload":"today+5"
          },
          {
            "content_type":"text",
            "title":fiveAfter,
            "payload":"today+5"
          }
        ]
      }
    }),

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

def order_prompt(token, recipient, text):
#leverage quick reply buttons to make sure they want to place an order

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message":{
        "text":"Hi there! I'm the Chicos Market Delivery Bot. Would you like to place an order?",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"Yes, let's order",
            "payload":"yesOrder"
          },
          {
            "content_type":"text",
            "title":"Naw",
            "payload":"noOrder"
          }
        ]
      }
    }),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def initial_item_prompt(token, recipient, text):
#leverage quick reply buttons to make sure they want to place an order

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message":{
        "text":"Choose which broad item you'd like to browse first, and then I'll show you some options to order!",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"Bread!",
            "payload":"sendBreads"
          },
          {
            "content_type":"text",
            "title":"Milk!",
            "payload":"sendMilks"
          },
          {
            "content_type":"text",
            "title":"Beer!",
            "payload":"sendBeers"
          },
          {
            "content_type":"text",
            "title":"Water!",
            "payload":"sendWaters"
          },
          {
            "content_type":"text",
            "title":"Pasta!",
            "payload":"sendPasta"
          },
          {
            "content_type":"text",
            "title":"Meats!",
            "payload":"sendMeats"
          },
          {
            "content_type":"text",
            "title":"Coffee Beans!",
            "payload":"sendCoffeeBeans"
          },
          {
            "content_type":"text",
            "title":"Hmm...what else?",
            "payload":"sendNextSet"
          }
        ]
      }
    }),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def followUp_item_prompt(token, recipient, text):
#leverage quick reply buttons to make sure they want to place an order

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message":{
        "text":"Where to start for your next item? If you're not feeling something else, you can just checkout, too.",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"Bread!",
            "payload":"sendBreads"
          },
          {
            "content_type":"text",
            "title":"Milk!",
            "payload":"sendMilks"
          },
          {
            "content_type":"text",
            "title":"Beer!",
            "payload":"sendBeers"
          },
          {
            "content_type":"text",
            "title":"Water!",
            "payload":"sendWaters"
          },
          {
            "content_type":"text",
            "title":"Pasta!",
            "payload":"sendPasta"
          },
          {
            "content_type":"text",
            "title":"Meats!",
            "payload":"sendMeats"
          },
          {
            "content_type":"text",
            "title":"Coffee Beans!",
            "payload":"sendCoffeeBeans"
          },
          {
            "content_type":"text",
            "title":"Hmm...what else?",
            "payload":"sendNextSet"
          }
        ]
      }
    }),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

def available_times(token, recipient, text, date):
#leverage quick reply buttons to book a time window 
#In the future, this will have to query some other database

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message":{
        "text":"These are the available time slots. Which works best?",
        "quick_replies":[
          {
            "content_type":"text",
            "title":"%s Time1: 3-4pm" % date,
            "payload":"time+1"
          },
          {
            "content_type":"text",
            "title":"%s Time2: 4-5pm" % date,
            "payload":"time+2"
          },
          {
            "content_type":"text",
            "title":"%s Time3: 5-6pm" % date,
            "payload":"time+3"
          }
        ]
      }
    }),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

# def available_time_windows(token, recipient, text, date):
#   """Send the ask for confirmation
#   """

#   r = requests.post("https://graph.facebook.com/v2.6/me/messages",
#     params={"access_token": token},
#     data=json.dumps({
#       "recipient": {"id": recipient},
#       "message": {"text": "Awesome. Here are the available time windows on %s" % date}
# }),

#     headers={'Content-type': 'application/json'})
#   if r.status_code != requests.codes.ok:
#     print r.text

def wrapUpMessage2(token, recipient, text, date, time):
  """Last message (payment integration would happen first)
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": "See you on %s between %s! Call us at 1(415)111-1111 if you need our help!" % (date,time)}
}),

    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

#we can make this a generic carousel that can send for any product chosen, we just need a dictionary
#with the appropriate data structure that keys off of what the user inputs in the initial prompt
def browse_set1(token, recipient, text, orderedItem):
  """Send carousel of products
  """
  item1_1         = orderedItem + "1.1"
  item1_2         = orderedItem + "1.2"
  item1_3         = orderedItem + "1.3"
  item1_4         = orderedItem + "1.4"
  item1_5         = orderedItem + "1.5"
  
  take_back_thing = "Eh, don't want %s" % orderedItem
  #figure the custom payload later
  #payloadOne = foods[orderedItem][item]
  #payloadX   = "X"   + orderedItem


  #r = requests.post("https://graph.facebook.com/v2.6/me/messages",
  #  params={"access_token": token},
  #  data=json.dumps(
  in_data={
    "message":{
      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"generic",
          "elements":[
              {
              "title":foods[orderedItem][item1_1]["title"],
              "image_url":foods[orderedItem][item1_1]["image_url"],
              "subtitle":foods[orderedItem][item1_1]["subtitle"],
              "buttons":[
                {
                "type":"postback",
                "title":"I want 1",
                "payload":foods[orderedItem][item1_1]["forPayloadOne"]
                },
                {
                "type":"postback",
                "title":"I want more than 1",
                "payload":"MoreCiabatta"
                },
                {
                "type":"postback",
                "title": take_back_thing,
                "payload":"back2categories"
                }
                ]
              },
              {
              "title":foods[orderedItem][item1_2]["title"],
              "image_url":foods[orderedItem][item1_2]["image_url"],
              "subtitle":foods[orderedItem][item1_2]["subtitle"],
              "buttons":[
                {
                "type":"postback",
                "title":"I want 1",
                "payload":foods[orderedItem][item1_2]["forPayloadOne"]
                },
                {
                "type":"postback",
                "title":"I want more than 1",
                "payload":"MoreSour"
                },
                {
                "type":"postback",
                "title": take_back_thing,
                "payload":"back2categories"
                }
                ]
            },
            {
            "title":foods[orderedItem][item1_3]["title"],
              "image_url":foods[orderedItem][item1_3]["image_url"],
              "subtitle":foods[orderedItem][item1_3]["subtitle"],
              "buttons":[
                {
                "type":"postback",
                "title":"I want 1",
                "payload":foods[orderedItem][item1_3]["forPayloadOne"]
                },
                {
                "type":"postback",
                "title":"I want more than 1",
                "payload":"MoreWheat"
                },
                {
                "type":"postback",
                "title":take_back_thing,
                "payload":"back2categories"
                }
                ]
            }
          ]
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
    #headers={'Content-type': 'application/json'})
  
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