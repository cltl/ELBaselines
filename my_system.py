import re
import sys
import urllib.parse
import urllib.request
import requests
import Levenshtein
import utils
from collections import OrderedDict, defaultdict
import redis
import pickle
from py2neo import Graph

rds=redis.Redis(socket_timeout=5)
def getPreviousOccurrence(c, entities):
	eid=len(entities)
	while eid>0:
		if entities[str(eid)]==c:
			return eid
		eid-=1
	return -1

def maxCoherence(w, l):
	m=0.0
	c=0
	while c<l:
		m+=w[str(c)]
		c+=1
	return m

def reread(resolvedMentions, entities, start, allCandidates, allMentions, weights, factorWeights, maxCount):
	while start<=len(entities):
		mention=allMentions[str(start)]
		allCandidates[str(start)]=moreLocalCandidates(mention, resolvedMentions, allCandidates[str(start)])
		myLink, score=disambiguateEntity(allCandidates[str(start)], weights, entities, factorWeights, maxCount)
		print(entities[str(start)], myLink)
		entities[str(start)]=myLink
		start+=1
	return entities

def disambiguateEntity(candidates, weights,resolvedEntities, factorWeights, maxCount):
	if len(candidates):
		max_score=0.4
		aging_factor=0.1
		best_candidate=None
		for cand in candidates:
			candidate=cand[0]
			ss=cand[1]["ss"]
			associativeness=cand[1]["count"]/maxCount
#			normalizationFactor=maxCoherence(weights, min(10,len(resolvedEntities)))
			normalizationFactor=1.0
			coherence=computeCoherence(candidate, resolvedEntities, weights)/normalizationFactor
			lastId=getPreviousOccurrence(candidate, resolvedEntities)
			recency=0.0
			if lastId>-1:				
				age=len(resolvedEntities)+1-lastId
				recency=(1-aging_factor)**age
			score=factorWeights['wss']*ss+factorWeights['wc']*coherence+factorWeights["wa"]*associativeness+factorWeights['wr']*recency
			print("%s\t%f\tss:%f, coh:%f, assoc:%f, recency:%f" % (candidate, score, ss, coherence, associativeness, recency))
			if score>max_score and not isDisambiguation(candidate):
				max_score=score
				best_candidate=candidate
		print("BEST CANDIDATE: %s" % best_candidate)
		return utils.normalizeURL(best_candidate), max_score
	else:
		return "--NME--", 1.0

def isDisambiguation(c):
        query='select ?b where { <' + c + '> <http://dbpedia.org/ontology/wikiPageDisambiguates> ?b } LIMIT 1'
        l=len(get_dbpedia_results(query))
        return l

def get_dbpedia_results(query):
	q = {'query': query, 'format': 'json'}
	s='http://dbpedia.org/sparql'
	url = s + '?' + urllib.parse.urlencode(q)
	#print url
	r = requests.get(url=url)
	try:
        	page = r.json()
        	return page["results"]["bindings"]
	except ValueError:
		return []

def shouldITry(maxi, s, other_id, current_id, weights):
        if maxi<=0.0:
                return True
        while other_id<=min(len(weights), current_id-1):
                s+=weights[str(other_id)]
                other_id+=1
        if s>maxi:
                return True
        else:
                return False

def computeCoherence(newEntity, previousEntities, w):
	total=0.0
	current_id=len(previousEntities)+1
	other_id=current_id-1
	while other_id>0 and str(current_id-other_id) in w:
		diff=current_id-other_id
		weight=w[str(diff)]
		max_score=0.0
		if diff==1 or shouldITry(max_score, total, diff, current_id, w):
	#                       total+=computePairCoherence(graph.node[other_id]['eid'], newEntity.replace('http://dbpedia.org/resource/', ''), weight)
			if previousEntities[str(other_id)]!='--NME--':
				total+=computeShortestPathCoherence(previousEntities[str(other_id)], utils.normalizeURL(newEntity), weight)
			other_id-=1
		else:
			break
	return total

def computeShortestPathCoherence(node1, node2, w):
	"""Connects to graph database, then creates and sends query to graph 
	database. Returns the shortest path between two nodes.
	Format: (67149)-[:'LINKS_TO']->(421)"""

	if node1.strip()==node2.strip():
		return w

	fromCache=rds.get("%s:%s" % (node1, node2))
	if fromCache:
		return float(fromCache)*w
	else:
		g = Graph()
		q="MATCH path=shortestPath((m:Page {name:\"%s\"})-[LINKS_TO*1..10]-(n:Page {name:\"%s\"})) RETURN LENGTH(path) AS length, path, m, n" % (node1, node2)

		cursor=g.run(q)
		path=None
		for c in cursor:
			path=c

	#
	#    print(("\nShortest Path:", path))
		if path:
			rds.set("%s:%s" % (node1, node2), 1/path["length"])
			rds.set("%s:%s" % (node2, node1), 1/path["length"])
			return w/path["length"]
		else:
			rds.set("%s:%s" % (node1, node2), 0.0)
			rds.set("%s:%s" % (node2, node1), 0.0)
			return 0.0


def is_abbrev(abbrev, text):

    abbrev=abbrev.replace('.', '')
    abbrev=abbrev.lower()
    text=text.lower()
    words=text.split()
    if not abbrev:
        return True
    if abbrev and not text:
        return False
    if abbrev[0]!=text[0]:
        return False
    else:
        return (is_abbrev(abbrev[1:],' '.join(words[1:])) or
                any(is_abbrev(abbrev[1:],text[i+1:])
                    for i in range(len(words[0]))))

def moreLocalCandidates(m, previous, candidates):
	for pm, pl in previous.items():
		print(m, pm)
		if is_abbrev(m, pm):
			for prevLink in previous[pm]:
				prevLink=utils.makeDbpedia(prevLink)
				print("Add %s for %s?" % (prevLink, m))
				if noCandidate(prevLink, candidates):
					print("YES")
					candidates.append(tuple([prevLink, {"ss": 1.0, "count": 0.0}]))
	return candidates

def noCandidate(newCand, cands):
	return not any(newCand==c1 for c1,c2 in cands)

def generateCandidatesWithLOTUS(mention, minSize=10, maxSize=100):
	normalized=utils.normalizeURL(mention)
	fromCache=rds.get("lotus:%s" % normalized)
	if fromCache:
		cands=pickle.loads(fromCache)
	else:
		cands=getCandidatesForLemma(mention, minSize, maxSize)
		cands=cleanRedirects(cands)
		rds.set("lotus:" + normalized, pickle.dumps(cands))
	sortedCands=sorted(cands.items(), key=lambda x:x[1]["ss"], reverse=True)
	try:
		maxCount=sorted(cands.items(), key=lambda x:x[1]["count"], reverse=True)[0][1]["count"]
	except:
		maxCount=1
	return sortedCands, maxCount

def getCandidatesForLemma(lemma, min_size, max_size):
	hits=[]
	for match in ["phrase", "conjunct"]:
		url="http://lotus.lodlaundromat.org/retrieve?size=" + str(max_size) + "&match=" + match + "&rank=psf&noblank=true&" + urllib.parse.urlencode({"string": lemma, "predicate": "label", "subject": "\"http://dbpedia.org/resource\""})
		r = requests.get(url=url)
		#print(r)
		content = r.json()

		these_hits=content["hits"]
		hits=hits + these_hits
		if content["numhits"]>=min_size or len(lemma.split(' '))==1:
			break

	subjects={}
	for hit in hits:
		lev_sim=Levenshtein.ratio(hit["string"], lemma)
		if "Disambiguation" not in hit["subject"].lower() and "Category" not in hit["subject"]:
			if hit["subject"] not in subjects:
				#subjects[hit["subject"]]=hit["length"]*len(lemma.split())
				subjects[hit["subject"]]={"ss": lev_sim, "count": 1}
			else:
				subjects[hit["subject"]]["ss"]=max(subjects[hit["subject"]]["ss"], lev_sim)
				subjects[hit["subject"]]["count"]+=1
	return subjects

def cleanRedirects(c):
        new_cands={}
        for link in c:
                if 'http://dbpedia.org/resource' not in link:
                        continue
                response = requests.get(link.replace('resource', 'page'))
                if response.history:
                # redirects
                        new_link=response.url.replace('page', 'resource')
                        #print(link, new_link)
                        if new_link in new_cands:
                                new_cands[new_link]["ss"]=max(new_cands[new_link]["ss"], c[link]["ss"])
                                new_cands[new_link]["count"]+=1
                        else:
                                new_cands[new_link]={"ss": c[link]["ss"], "count": 1}
                else:
                        if response.status_code==200:
                                if link in new_cands:
                                        new_cands[link]["ss"]=max(new_cands[link]["ss"], c[link]["ss"])
                                        new_cands[link]["count"]+=1
                                else:
                                        new_cands[link]={"ss": c[link]["ss"], "count": 1}
        return new_cands

def computeWeights(n):
	i=0
	w={}
	total=n*(n+1)/2
	while i<n:
		w[str(i)]=1/n
		#w[str(i)]=(n-i)/total
		i+=1
	return w

def run(inFile, outFile, pickleFile, topic='WAR_CIVIL_WAR', factorWeights={'wss':0.4,'wc':0.4, 'wa':0.1, 'wr': 0.1}, topicAgg=True):
	#articles=['1314testb Third']
	topicsToArticles=pickle.load(open(pickleFile, 'rb'))
	articles=topicsToArticles[topic]
	print(articles)
	N=10
	weights=computeWeights(N)
	if topicAgg:
		print("Running per topic")
		runUnit(inFile, outFile, weights, articles, factorWeights)
	else:
		print("Running single articles")
		for article in articles:
			runUnit(inFile, outFile, weights, [article], factorWeights)

def runUnit(fn, outFile, weights, articles, factorWeights):
	myFile = open(fn, "r")
	minSize=20
	maxSize=200
	potential=0
	total=0
	resolvedEntities={}
	resolvedMentions=defaultdict(list)
	w=open(outFile, "a")
	allCandidates={}
	allMentions={}
	iterations=2
	lines={}
	for line in myFile:
		line=line.strip()
		for article in sorted(articles):
			article=article.strip().split()[0]
			if article in line:
				lineArray=line.split('\t')
				mention=lineArray[6]
				goldLink=lineArray[1]
				systemLink=lineArray[2]
				candidates, maxCount=generateCandidatesWithLOTUS(mention, minSize, maxSize)
				candidates=moreLocalCandidates(mention, resolvedMentions, candidates)
				print("###################################################################################")
				print("RESOLVING %s" % mention)
				print("###################################################################################")
				allCandidates[str(len(resolvedEntities)+1)]=candidates
				allMentions[str(len(resolvedEntities)+1)]=mention
				myLink, score=disambiguateEntity(candidates, weights, resolvedEntities, factorWeights, maxCount)
				lines[str(len(resolvedEntities)+1)]=line
				resolvedEntities[str(len(resolvedEntities)+1)]=myLink
				resolvedMentions[mention].append(myLink)
	iterations-=1
	while iterations>0:
		print("###################################################################################")
		print("###################################################################################")
		print("###################################################################################")
		print("REREADING..........")
		start=1
		resolvedEntities=reread(resolvedMentions,resolvedEntities,start, allCandidates, allMentions, weights, factorWeights, maxCount)
		while start<=len(resolvedEntities):
			w.write("%s\t%f\t%s\n" % (lines[str(start)], 0.0, resolvedEntities[str(start)]))
			start+=1
		iterations-=1
if __name__=='__main__':
	run(sys.argv[1])
