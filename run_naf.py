import utils
import dis_agdistis
import os
import sys

if __name__=="__main__":
	corpus=sys.argv[1]
	same=0
	notSame=0
	myConll=""
	for file in os.listdir(corpus):
		if not file.endswith(".xml") and not file.endswith(".naf"):
			continue
		print(file)
		filename=corpus.strip('/') + '/' + file
		myXml, entities=utils.naf2inlineEntities(filename, True)
		print(myXml)
		print(entities)
		da=dis_agdistis.disambiguate(myXml, "agdistis")
		for agd_entity in da:
			print(agd_entity)
			offset=str(agd_entity["start"])
			agd_link=str(agd_entity["disambiguatedURL"])
			goldlink=str(entities[offset])
			id=file + offset
			myConll+="%s\t%s\t%s\n" % (id, goldlink, agd_link)
	p, r, f1=utils.computePRF(myConll)
	
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f1))
