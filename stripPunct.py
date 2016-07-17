import string
def noPunct(myList):
	for pair in myList:
		for item in pair:
				item = removePunctuation(item)

def removePunctuation(myString):
	punct = set(string.punctuation)
	myString = ''.join(c for c in myString if c not in punct)
	return myString