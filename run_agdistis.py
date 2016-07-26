#!/usr/bin/python

# Filip Ilievski
# July 2016

import utils
import dis_agdistis
import os
import sys

def run(corpus, myFile, topic, aggregateTopics):
	if not os.path.isfile(myFile):
		entitiesNumber=0
		with open(corpus, "r") as myCorpus:
			currentArticle=""
			currentTopic=""
			myConll=""
			openEntity=False
			articleEntities=0
			registeredEntities=0
			relevant=False
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
							for agd_entity in sorted(da, key=lambda k: k['start']):
								offset=str(agd_entity["start"])
								agd_link=utils.normalizeURL(agd_entity["disambiguatedURL"])
								goldlink=utils.checkRedirects(utils.normalizeURL(goldEntities[offset]))
								id=currentArticle + offset
								mention=goldMentions[offset]
								v1,v2=utils.getRanks(goldlink, agd_link)
								print(v1, v2)
								myConll+="%s\t%s\t%s\t%s\t%f\t%f\t%s\n" % (id, goldlink, agd_link, currentTopic, v1, v2, mention)
						testB=True
						line=line.strip()
						articleInfo=line.split('\t')
						currentArticle=articleInfo[0]
						currentTopic=articleInfo[1]
						if aggregateTopics and topic!=currentTopic:
							relevant=False
						else:
							relevant=True
							print("Article %s has topic %s." % (currentArticle, currentTopic))
						if not aggregatedTopics:
							offset=0
							tid=1
							allTokens={}
							goldEntities={}
							goldMentions={}
					else:
						testB=False
				elif testB and relevant:
					tokenInfo=line.split('\t')
					text=tokenInfo[0]
					if tokenInfo[1].strip()!='I' and openEntity is True:
						openEntity=False	
						allTokens[str(tid-1)]['text']+='</entity>'
						registeredEntities+=1
					if tokenInfo[1].strip()=='B':
						goldMentions[str(offset)]=tokenInfo[2].strip()
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
			for agd_entity in sorted(da, key=lambda k: k['start']):
				offset=str(agd_entity["start"])
				agd_link=utils.normalizeURL(agd_entity["disambiguatedURL"])
				goldlink=utils.checkRedirects(utils.normalizeURL(goldEntities[offset]))
				mention=goldMentions[offset]
				id=currentArticle + offset
				v1,v2=utils.getRanks(goldlink, agd_link)
				myConll+="%s\t%s\t%s\t%s\t%f\t%f\t%s\n" % (id, goldlink, agd_link, currentTopic, v1, v2, mention)

		print(entitiesNumber)	
		w=open(myFile, "a")
		w.write(myConll)
	p, r, f1=utils.computeStats(myFile)
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f1))

