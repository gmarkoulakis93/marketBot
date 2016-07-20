import csv
def findCity(recipient):
	with open('sender_file.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['m_id']==recipient:
				return row['city']
			pass
def findPostal(recipient):
	with open('sender_file.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['m_id']==recipient:
				return row['postal_code']
			pass
def findStreet(recipient):
	with open('sender_file.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['m_id']==recipient:
				return row['street_1']
			pass
def findFName(recipient):
	with open('sender_file.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['m_id']==recipient:
				return row['fname']
			pass
def findLName(recipient):
	with open('sender_file.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['m_id']==recipient:
				return row['lname']
			pass