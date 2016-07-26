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
		corpus=corpus.strip('/')
		for file in os.listdir(corpus):
			if not file.endswith(".xml") and not file.endswith(".naf"):
				continue
			print(file)
			filename=corpus + '/' + file
			myXml, entities, mentions=utils.naf2inlineEntities(filename, True)
			da=dis_agdistis.disambiguate(myXml, "agdistis")
			for agd_entity in da:
				offset=str(agd_entity["start"])
				agd_link=utils.normalizeURL(str(agd_entity["disambiguatedURL"]))
				goldlink=utils.checkRedirects(utils.normalizeURL(str(entities[offset])))
				id=file + offset
				v1,v2=utils.getRanks(goldlink, agd_link)
				mention=mentions[offset]
				myConll+="%s\t%s\t%s\t%s\t%f\t%f\t%s\n" % (id, goldlink, agd_link, corpus, v1, v2, mention)
		w=open(myFile, "w")
		w.write(myConll)
	p, r, f1=utils.computeStats(myFile)
	
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f1))
