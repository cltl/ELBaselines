from flask import Flask, request, Response
from rdflib import Graph, URIRef
app = Flask(__name__)
import pickle
import nif_system

#fullText = URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#isString")
#entityMention = URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#anchorOf")
mimetype='application/x-turtle'

w=open('flask.log', 'a')

@app.route("/<int:iterations>/<int:memory>", methods = ['POST'])
def run(iterations, memory):
	global num
	print("Request %d came! %d iterations, Memory: %r" % (num, iterations, memory>0))
	num+=1
	g=Graph()
	inputRDF=request.stream.read()
	w.write(str(inputRDF) + '\n')
	g.parse(data=inputRDF, format="n3")

	factorWeights={'wc':0.525,'wss': 0.325, 'wa': 0.05, 'wr':0.05, 'wt': 0.05}
	timePickle=pickle.load(open('200712_agg.p', 'rb'))

	global lastN
	if memory>0:
		g,lastN=nif_system.run(g, factorWeights, timePickle, iterations, lastN)
	else:
		lastN=[]
		g,lastN=nif_system.run(g, factorWeights, timePickle, iterations, lastN)


	outputRDF=g.serialize(format='turtle')
	#for s,p,o in g.triples( (None, fullText, None) ):
	#	print("%s has text %s" % (s, o))
	#for s,p,o in g.triples( (None, entityMention, None) ):
	#	print("%s has mention %s" % (s, o))
	w.write(str(outputRDF) + '\n')
	return Response(outputRDF, mimetype=mimetype)

if __name__ == "__main__":
	global num
	num=0
	global lastN
	lastN=[]
	app.run()
