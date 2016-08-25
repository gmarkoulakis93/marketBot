import string

punct = set(string.punctuation)

def noPunct(myList):
	for pair in myList:
		for item in pair:
				item = removePunctuation(item)

def removePunctuation(myString):	
	myString = ''.join(c for c in myString if c not in punct)
	return myString