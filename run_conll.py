#!/usr/bin/python

# Filip Ilievski
# July 2016

import utils
import dis_agdistis
import os
import sys

if __name__=="__main__":
	if len(sys.argv)<3:
		print("Not enough arguments!!!")
		print("python run_conll.py {CORPUS/PATH} {FILENAME.TSV}")
		sys.exit(1)
	corpus=sys.argv[1]
	myFile=sys.argv[2]
	if not os.path.isfile(myFile):
		entitiesNumber=0
		with open(corpus, "r") as myCorpus:
			currentArticle=""
			currentTopic=""
			myConll=""
			openEntity=False
			articleEntities=0
			registeredEntities=0
			for line in myCorpus:
				if line.startswith("-DOCSTART-"):
					if 'testb' in line:
						if currentArticle!="":
							if openEntity:
								openEntity=False
								allTokens[str(tid-1)]['text']+='</entity>'
								registeredEntities+=1
							if registeredEntities<articleEntities:
								print(registeredEntities, articleEntities)
								sys.exit(0)
							articleEntities=0
							registeredEntities=0
							myXml=utils.composeText(allTokens)
							da=dis_agdistis.disambiguate(myXml, "agdistis")
							for agd_entity in da:
								offset=str(agd_entity["start"])
								agd_link=utils.normalizeURL(agd_entity["disambiguatedURL"])
								goldlink=utils.checkRedirects(utils.normalizeURL(goldEntities[offset]))
								print(agd_link, goldlink)
								id=currentArticle + offset
								myConll+="%s\t%s\t%s\n" % (id, goldlink, agd_link)
						testB=True
						line=line.strip()
						articleInfo=line.split('\t')
						currentArticle=articleInfo[0]
						currentTopic=articleInfo[1]
						print("Article %s has topic %s." % (currentArticle, currentTopic))
						offset=0
						tid=1
						allTokens={}
						goldEntities={}
					else:
						testB=False
				elif testB:
					tokenInfo=line.split('\t')
					text=tokenInfo[0]
					if tokenInfo[1].strip()!='I' and openEntity is True:
						openEntity=False	
						allTokens[str(tid-1)]['text']+='</entity>'
						registeredEntities+=1
					if tokenInfo[1].strip()=='B':
						entitiesNumber+=1
						articleEntities+=1
						if tokenInfo[3]=='--NME--':
							goldEntities[str(offset)]=tokenInfo[3]
						else:
							goldEntities[str(offset)]=tokenInfo[4]
						text='<entity>' + text
						if tokenInfo[0].strip()==tokenInfo[2].strip():
							text+='</entity>'
							registeredEntities+=1
						else:
							openEntity=True
					
					allTokens[str(tid)]={'text': text, 'offset': str(offset)}
					offset+=len(tokenInfo[0]) + 1
					tid+=1

			if openEntity:
				allTokens[str(tid-1)]['text']+='</entity>'
				registeredEntities+=1
			if registeredEntities<articleEntities:
				print(registeredEntities, articleEntities)
				sys.exit(0)
			myXml=utils.composeText(allTokens)
			da=dis_agdistis.disambiguate(myXml, "agdistis")
			for agd_entity in da:
				offset=str(agd_entity["start"])
				agd_link=utils.normalizeURL(agd_entity["disambiguatedURL"])
				goldlink=utils.checkRedirects(utils.normalizeURL(goldEntities[offset]))
				print(agd_link, goldlink)
				id=currentArticle + offset
				myConll+="%s\t%s\t%s\n" % (id, goldlink, agd_link)

		print(entitiesNumber)	
		w=open(myFile, "w")
		w.write(myConll)
	p, r, f1=utils.computePRF(myFile)
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f1))
