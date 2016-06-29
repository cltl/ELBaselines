#!/usr/bin/python

# Filip Ilievski
# June 2016 

from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json

disambiguatorUrl="http://139.18.2.164:8080/AGDISTIS"

def disambiguate(xmlText, type='agdistis'):
	params={"text": xmlText, "type": type}
	request = Request(disambiguatorUrl, urlencode(params).encode())
	thisJson = urlopen(request).read().decode()
	return json.loads(thisJson)

if __name__ == '__main__':

	with open('zeppelin.txt', 'r') as myfile:
		text=myfile.read().replace('\n', '')

	disambiguate(text, "agdistis")
