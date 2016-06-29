import utils
import dis_agdistis
import os
import sys

if __name__=="__main__":
	corpus=sys.argv[1]
	same=0
	notSame=0
	for file in os.listdir(corpus):
		print(file)
		filename=corpus.strip('/') + '/' + file
		myXml, entities=utils.naf2inlineEntities(filename)
		print(myXml)
		print(entities)
		da=dis_agdistis.disambiguate(myXml, "agdistis")
		for agd_entity in da:
			print(agd_entity)
			offset=str(agd_entity["start"])
			agd_link=str(agd_entity["disambiguatedURL"])
			goldlink=str(entities[offset])
			print(agd_link, goldlink)
			if agd_link==goldlink:
				same+=1
			else:
				notSame+=1
			

		break
	print("Same: %d. Not same: %d. Accuracy: %f" % (same, notSame, same/(same+notSame)))
