import utils
import dis_agdistis
import os
import sys

if __name__=="__main__":
	corpus=sys.argv[1]
	for file in os.listdir(corpus):
		print(file)
		filename=corpus.strip('/') + '/' + file
		myXml, entities=utils.naf2inlineEntities(filename)
		print(myXml)
		print(entities)
		dis_agdistis.disambiguate(myXml, "agdistis")
		for agd_entity in da:
			offset=str(agd_entity["start"])
			agd_link=agd_entity["disambiguatedURL"]
			if agd_link==goldlink:
				print("same")
			else:
				print("not same")
			

		break
