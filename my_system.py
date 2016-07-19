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

def disambiguateEntity(currentEntity, candidates, weights,resolvedEntities):
	if len(candidates):
		max_score=-0.1
		best_candidate=None
		for cand in candidates:
			score=cand[1]["ss"]
			candidate=cand[0]
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

def computeCoherence(newEntity, current_id, graph, w, max_score):
        total=0.0
        other_id=current_id-1
        while other_id>0 and str(current_id-other_id) in w:
                #print(other_id)
                diff=current_id-other_id
                weight=w[str(diff)]
                if current_id<6:
                        weight*=len(w)/(current_id-1) # Normalize for the cases where there less than N previous entities (only in the beginning)
                        print("%d is the current ID, weight value is: %f" % (current_id, weight))
                #weight=1/len(w)
                if diff==1 or shouldITry(max_score, total, diff, current_id, w):
#                       total+=computePairCoherence(graph.node[other_id]['eid'], newEntity.replace('http://dbpedia.org/resource/', ''), weight)
                        total+=computeShortestPathCoherence(graph.node[other_id]['eid'], newEntity.replace('http://dbpedia.org/resource/', ''), weight)
                        other_id-=1
                else:
                        break
        return total

def computeShortestPathCoherence(node1, node2, w):
    """Connects to graph database, then creates and sends query to graph 
    database. Returns the shortest path between two nodes.
    Format: (67149)-[:'LINKS_TO']->(421)"""

    if node1.strip()==node2.strip():
        print("It's the same thing: %s" % (node1))
        return w

    g = Graph()
    q="MATCH path=shortestPath((m:Page {name:\"%s\"})-[LINKS_TO*1..10]-(n:Page {name:\"%s\"})) RETURN LENGTH(path) AS length, path, m, n" % (node1, node2)

    cursor=g.run(q)
    path=None
    for c in cursor:
        path=c

#
#    print(("\nShortest Path:", path))
    if path:
        return w/path["length"]
    else:
        return 0.0



def generateCandidatesWithLOTUS(mention, minSize=10, maxSize=100):
	rds=redis.Redis()
	normalized=utils.normalizeURL(mention)
	fromCache=rds.get("lotus:%s" % normalized)
	if fromCache:
		cands=pickle.loads(fromCache)
		print("CACHED", mention, cands)
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
		else:
			print("%d hits so far, after the %s matching. We need more candidates..." % (content["numhits"], match))

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
	w=[]
	while i<n:
		w.append(1/n)
		i+=1
	return w

if __name__=='__main__':
	topic='WAR_CIVIL_WAR'
	fn=sys.argv[1]
	#articles=['1314testb Third']
	articles=['1314testb Third', '1212testb GUNMEN', '1313testb Italy', '1304testb Turkey', '1305testb Three', '1332testb Burmese', '1317testb Moslem', '1266testb Government', '1267testb Burmese']
	file = open(fn, "r")
	minSize=20
	maxSize=200
	potential=0
	total=0
	N=5
	weights=computeWeights(N)
	resolvedEntities={}
	w=open("aidaMyOutput.tsv", "w")
	for line in file:
		line=line.strip()
		for article in sorted(articles):
			if re.search(article, line):
				lineArray=line.split('\t')
				mention=lineArray[6]
				goldLink=lineArray[1]
				systemLink=lineArray[2]
				candidates, maxCount=generateCandidatesWithLOTUS(mention, minSize, maxSize)
				myLink=disambiguateEntity(mention, candidates, weights, resolvedEntities)
				print(mention, goldLink, systemLink, myLink)
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

	p, r, f=utils.computeStats("aidaMyOutput.tsv", False)
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
