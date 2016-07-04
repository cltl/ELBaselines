#!/usr/bin/python

# Filip Ilievski
# June 2016

import utils
import dis_agdistis
import os
import sys

if __name__=="__main__":
	if len(sys.argv)<3:
		print("Not enough arguments!!!")
		print("python run_naf.py {CORPUS/PATH} {FILENAME.TSV}")
		sys.exit(1)
	corpus=sys.argv[1]
	myFile=sys.argv[2]
	if not os.path.isfile(myFile):
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
				agd_link=utils.normalizeURL(str(agd_entity["disambiguatedURL"]))
				goldlink=utils.normalizeURL(str(entities[offset]))
				id=file + offset
				myConll+="%s\t%s\t%s\n" % (id, goldlink, agd_link)
		w=open(myFile, "w")
		w.write(myConll)
	p, r, f1=utils.computePRF(myFile)
	
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f1))
