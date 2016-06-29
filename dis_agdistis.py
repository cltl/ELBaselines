#!/usr/bin/python

# Filip Ilievski
# June 2016 

from urllib.parse import urlencode
from urllib.request import urlopen, Request

disambiguatorUrl="http://139.18.2.164:8080/AGDISTIS"

def disambiguate(xmlText, type='agdistis'):
	params={"text": xmlText, "type": type}
	request = Request(disambiguatorUrl, urlencode(params).encode())
	json = urlopen(request).read().decode()
	print(json)

if __name__ == '__main__':

	with open('zeppelin.txt', 'r') as myfile:
		text=myfile.read().replace('\n', '')

	disambiguate(text, "agdistis")
