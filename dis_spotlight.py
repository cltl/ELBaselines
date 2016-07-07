#!/usr/bin/python

# Filip Ilievski
# June 2016 

from urllib.parse import urlencode
from urllib.request import urlopen

spotlightUrl="http://spotlight.dbpedia.org/annotate/"

def disambiguate(xmlText):
	params={"spotter": "SpotXmlParser", "text": xmlText}
	encodedParams=urlencode(params)
#	encodedParams=params
	reqUrl=spotlightUrl + "?" + encodedParams
	print(reqUrl)
	res=urlopen(reqUrl)
	print(res)

def usingSplit2(line, _len=len):
	words = line.split()
	index = line.index
	offsets = []
	append = offsets.append
	running_offset = 0
	for word in words:
		word_offset = index(word, running_offset)
		word_len = _len(word)
		running_offset = word_offset + word_len
		append((word, word_offset, running_offset - 1))
	return offsets

def prepareSpotlightXml(text, mentions):
	myXml="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
	
	myXml+="<annotation text=\"%s\">" % text
	for m in mentions:
		myXml+="<surfaceForm name=\"%s\" offset=\"%s\" />" % (m[0], m[1])

	return myXml


with open('examples/example.txt', 'r') as myfile:
	text=myfile.read().replace('\n', '')

print(text)
offsets=usingSplit2(text)
print(offsets)
mentions=[]
mentions.append(tuple(["European", "54"]))
xmlText=prepareSpotlightXml(text, mentions)
print(xmlText)
disambiguate(xmlText)
