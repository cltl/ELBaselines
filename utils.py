import sys
from KafNafParserPy import *

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

def composeText(jsonFile):
	count=1
	readyText=''
	while True:
		if str(count) in jsonFile:
			readyText+=jsonFile[str(count)]['text'] + ' '
			count+=1
		else:
			break
	return readyText.strip()

def getStartEndEntityTokens(entity, myParser):
	for ref in entity.get_references():
		terms=ref.get_span().get_span_ids()
	tokens=[]
	for termId in terms:
		termObject=myParser.get_term(termId)
		for tokenId in termObject.get_span().get_span_ids():
			tokens.append(int(tokenId))
		
	return min(tokens), max(tokens)

def naf2inlineEntities(filename, overlap=False):
	myParser=KafNafParser(filename)
	allTokens={}
	offset=0
	for word in myParser.get_tokens():
		allTokens[word.get_id()]={'text': word.get_text(), 'offset': offset}
		offset+=len(word.get_text()) + 1
	print(allTokens)

	pastEntityTerms=[]
	goldEntities={}
	for entity in myParser.get_entities():
		mini, maxi = getStartEndEntityTokens(entity, myParser)
		if overlap or (mini not in pastEntityTerms and maxi not in pastEntityTerms):
			allTokens[str(mini)]['text'] = '<entity>' + allTokens[str(mini)]['text']
			allTokens[str(maxi)]['text'] = allTokens[str(maxi)]['text'] + '</entity>'
			pastEntityTerms.append(maxi)
			pastEntityTerms.append(mini)
			for extRef in entity.get_external_references():
				goldEntities[str(allTokens[str(mini)]["offset"])]= extRef.get_reference()
	return composeText(allTokens), goldEntities

def normalizeURL(s):
	return s.replace("http://en.wikipedia.org/wiki/", "").replace("http://dbpedia.org/resource/", ""). replace("http://dbpedia.org/page/", "").lower().strip()

def computePRF(fn):
	myConll=open(fn, "r")
	tp=0
	fp=0
	fn=0
	for sf in myConll:
		sfPieces=sf.split()
		gold=sfPieces[1]
		system=sfPieces[2]
		print(gold, system)
		if system==gold:
			tp+=1
		else:
			if system not in ["none", "nill"]:
				fp+=1
			if gold not in ["none", "nill"]:
				fn+=1

	print(tp, fp, fn)
	prec=tp/(tp+fp)
	recall=tp/(tp+fn)
	f1=2*prec*recall/(prec+recall)
	
	return prec, recall, f1
