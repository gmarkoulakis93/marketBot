def stripPunct(myList):
	punct = set(string.punctuation)
	x = 0
	for item in myList[x][0]:
		for i in punct:
			if i in myList[x][0]:
				myList[x][0] = myList[x][0].replace(i,"").strip()
		x = x +1
	x = 0
	for item in myList[x][1]:
		for i in punct:
			if i in myList[x][1]:
				myList[x][1] = myList[x][1].replace(i,"").strip()
		x = x +1