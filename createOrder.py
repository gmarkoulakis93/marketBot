def createOrder(tuples, inventory, order):
	x = 0
	while x < len(tuples):
		for thing in inventory:
			if thing in tuples[x][1]:
				order.append(tuples[x])
			else:
				pass
		x = x+1