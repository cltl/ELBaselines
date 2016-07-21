import re
import sys
import urllib.parse
import urllib.request
import requests
import Levenshtein
import utils
from collections import OrderedDict
import redis
import pickle
from py2neo import Graph

rds=redis.Redis(socket_timeout=5)
def disambiguateEntity(currentEntity, candidates, weights,resolvedEntities, factorWeights, maxCount):
	if len(candidates):
		max_score=-0.1
		best_candidate=None
		for cand in candidates:
			candidate=cand[0]
			ss=cand[1]["ss"]
			associativeness=cand[1]["count"]/maxCount
			coherence=computeCoherence(candidate, resolvedEntities, weights)
			score=factorWeights['wss']*ss+factorWeights['wc']*coherence+factorWeights["wa"]*associativeness
			if score>max_score and not isDisambiguation(candidate):
				max_score=score
				best_candidate=candidate
		return utils.normalizeURL(best_candidate)
	else:
		return "--NME--"

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
			return w/path["length"]
		else:
			rds.set("%s:%s" % (node1, node2), 0.0)
			return 0.0

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
		#w[str(i)]=1/n
		w[str(i)]=(n-i)/total
		i+=1
	return w

def run(fn, topic='WAR_CIVIL_WAR', factorWeights={'wss':0.4,'wc':0.4, 'wa':0.2}):
	#articles=['1314testb Third']
	topicsToArticles=pickle.load(open('topics.p', 'rb'))
	articles=topicsToArticles[topic]
	print(articles)
	myFile = open(fn, "r")
	minSize=20
	maxSize=200
	potential=0
	total=0
	N=10
	weights=computeWeights(N)
	resolvedEntities={}
	w=open("aidaMyOutput.tsv", "a")
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
				myLink=disambiguateEntity(mention, candidates, weights, resolvedEntities, factorWeights, maxCount)
				resolvedEntities[str(len(resolvedEntities)+1)]=myLink
				w.write("%s\t%s\n" % (line, myLink))
				"""
				if goldLink!='--NME--':
					if utils.makeDbpedia(goldLink) in candidates:
						potential+=1
						print("It exists as %d-th candidate" % list(candidates.keys()).index(utils.makeDbpedia(goldLink)))
				else:
					potential+=1
					print("There are %d candidates" % len(candidates))
				total+=1
	utils.computeUpperBound(potential, total))
				"""

	#p, r, f=utils.computeStats("aidaMyOutput.tsv", False)
	#print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
	#return f

if __name__=='__main__':
	run(sys.argv[1])
