#!/usr/bin/python

# Filip Ilievski
# June 2016

import sys
from KafNafParserPy import *
import redis
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict, Counter

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
nones=["none", "nil", "--nme--"]

def checkRedirects(e):
	rds=redis.Redis()
	fromCache=rds.get(e)
	if fromCache:
		print("CACHED", e, fromCache.decode())
		return fromCache.decode()
	else:
		sparql.setQuery("""
		select distinct ?c where {<http://dbpedia.org/resource/%s> <http://dbpedia.org/ontology/wikiPageRedirects> ?c}
		""" % e)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			red=str(result["c"]["value"])
			r=normalizeURL(red)
			rds.set(e,r)
			return r
		print("NO REDIRECT",e)
		rds.set(e,e)
		return e

def getRanks(e1, e2):
	return getRank(e1), getRank(e2)

def getRank(e):
	print("Looking for the rank of %s" % e)
	if e.lower() in nones:
		print("e is a none")
		return 0.0
	rds=redis.Redis()
	fromCache=rds.get("rank:%s" % e)
	
	if fromCache:
		print("CACHED", e, float(fromCache))
		return float(fromCache)
	else:
		elink=makeDbpedia(e)
		sparql.setQuery("""
			PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX dbo:<http://dbpedia.org/ontology/>

			PREFIX vrank:<http://purl.org/voc/vrank#>

			SELECT ?v
			FROM <http://dbpedia.org>
			FROM <http://people.aifb.kit.edu/ath/#DBpedia_PageRank>
			WHERE {
			<%s> vrank:hasRank/vrank:rankValue ?v.
			}
		""" % elink)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()

		for result in results["results"]["bindings"]:
			v=float(result["v"]["value"])
			print("Not cached: %f for %s" % (v, e))
			rds.set("rank:%s" % e, v)
			return v

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
	if s:
#                return s.encode('utf-8').decode('unicode_escape').replace("http://en.wikipedia.org/wiki/", "").replace("http://dbpedia.org/resource/", ""). replace("http://dbpedia.org/page/", "").strip()
		return s.replace("http://en.wikipedia.org/wiki/", "").replace("http://dbpedia.org/resource/", ""). replace("http://dbpedia.org/page/", "").strip()
	else:
		return '--NME--'

def makeDbpedia(x):
	return "http://dbpedia.org/resource/" + x

def computePRF(tp, fp, fn):
	prec=tp/(tp+fp)
	recall=tp/(tp+fn)
	f1=2*prec*recall/(prec+recall)
	return prec, recall, f1

def computeStats(fn, rankAnalysis=True, topicAnalysis=True):
	myConll=open(fn, "r")
	tp=0
	fp=0
	fn=0
	lenEnt=0
	goldNils=0
	systemNils=0
	goldPopular=0
	systemPopular=0
	systemRank=0.0
	goldRank=0.0
	aggregated_wrong={}
	aggregated_correct={}
	topicAcc=defaultdict(list)
	topicArticles=defaultdict(set)
	for sf in myConll:
		sfPieces=sf.split('\t')
		gold=sfPieces[1].strip()
		system=sfPieces[2].strip()
		currentTopic=sfPieces[3].strip()
		lenEnt+=1
		s=sfPieces[0].strip()
		currentArticle=s[s.find("(")+1:s.find(")")]
		topicArticles[currentTopic].add(currentArticle)
		if system.lower() in nones:
			systemNils+=1
		if gold.lower() in nones:
			goldNils+=1
		if system.lower()==gold.lower() or (system.lower() in nones and gold.lower() in nones):
			tp+=1
			topicAcc[currentTopic].append('tp');
			if gold.lower() in aggregated_correct:
                                aggregated_correct[gold.lower()]+=1
			else:
				aggregated_correct[gold.lower()]=1
		else:
			if system.lower() not in nones:
				fp+=1
				topicAcc[currentTopic].append('fp');
			if gold.lower() not in nones:
				fn+=1
				topicAcc[currentTopic].append('fn');
			if gold.lower() in aggregated_wrong:
				aggregated_wrong[gold.lower()]+=1
			else:
				aggregated_wrong[gold.lower()]=1
		if rankAnalysis and system.lower()!=gold.lower() and system.lower() not in nones and gold.lower() not in nones:
			vgold=float(sfPieces[4])
			vsys=float(sfPieces[5])
			if vsys>vgold:
				print("%s (system) is more popular than %s (gold)" % (system, gold))
				systemPopular+=1
			elif vsys<vgold:
				print("%s (gold) is more popular than %s (system)" % (gold, system))
				goldPopular+=1
			systemRank+=vsys
			goldRank+=vgold
			

	print("System more popular in %d cases. Gold more popular in %d cases" % (systemPopular, goldPopular))
	print("System rank total: %f. Gold rank total: %f." % (systemRank, goldRank))
	aggc = sorted(aggregated_correct.items(), key=lambda k: k[1], reverse=True)
	print("CORRECT:",aggc[:10])
	aggw = sorted(aggregated_wrong.items(), key=lambda k: k[1], reverse=True)
	print("WRONG:",aggw[:10])
	print("%d entities. %d gold nils, %d system nils" % (lenEnt, goldNils, systemNils))
	print(tp, fp, fn)

	print(topicAcc)
	for k,v in topicAcc.items():
		cntr=Counter(v)
		topicTp=cntr['tp']
		topicFn=cntr['fn']
		topicFp=cntr['fp']
		topicPrec, topicRecall, topicF1=computePRF(topicTp, topicFp, topicFn)
		print("Topic %s (%d articles), Precision: %s, Recall: %s, F1: %s" % (k, len(topicArticles[k]), topicPrec, topicRecall, topicF1))
	print(topicArticles)
	print(len(topicAcc))

	return computePRF(tp, fp, fn)
