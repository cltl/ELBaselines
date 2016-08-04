import sys
import time
import os
import utils
import my_system
import run_agdistis

if __name__=='__main__':
	aggregateTopics=True
	if sys.argv[1]=='top':
		topics=['GOVERNMENT/SOCIAL', 'CORPORATE/INDUSTRIAL TRADE/RESERVES ECONOMICS', 'GOVERNMENT_FINANCE ECONOMICS GOVERNMENT/SOCIAL', 'ECONOMICS', 'MANAGEMENT CORPORATE/INDUSTRIAL', 'MARKETS/MARKETING CORPORATE/INDUSTRIAL', 'FUNDING/CAPITAL CORPORATE/INDUSTRIAL EUROPEAN_COMMUNITY GOVERNMENT/SOCIAL', 'PERFORMANCE MARKETS/MARKETING CORPORATE/INDUSTRIAL', 'FUNDING/CAPITAL CORPORATE/INDUSTRIAL', 'MONETARY/ECONOMIC ECONOMICS MONEY_MARKETS MARKETS', 'EMPLOYMENT/LABOUR TRADE/RESERVES ECONOMICS GOVERNMENT/SOCIAL', 'MARKETS/MARKETING CORPORATE/INDUSTRIAL COMMODITY_MARKETS MARKETS', 'CORPORATE/INDUSTRIAL', 'CORPORATE/INDUSTRIAL COMMODITY_MARKETS MARKETS', 'ACCOUNTS/EARNINGS PERFORMANCE CORPORATE/INDUSTRIAL', 'MONEY_MARKETS MARKETS', 'CONTRACTS/ORDERS CORPORATE/INDUSTRIAL', 'MARKETS', 'MONETARY/ECONOMIC ECONOMICS EUROPEAN_COMMUNITY GOVERNMENT/SOCIAL', 'TRADE/RESERVES ECONOMICS', 'NONE', 'GOVERNMENT_FINANCE ECONOMICS', 'OWNERSHIP_CHANGES CORPORATE/INDUSTRIAL', 'COMMODITY_MARKETS MARKETS', 'MARKETS/MARKETING CORPORATE/INDUSTRIAL TRADE/RESERVES ECONOMICS EUROPEAN_COMMUNITY GOVERNMENT/SOCIAL', 'PERFORMANCE CORPORATE/INDUSTRIAL', 'CORPORATE/INDUSTRIAL GOVERNMENT/SOCIAL']
		inFile='CONLL/AIDA-YAGO2-dataset_topicsToplevel.tsv'
		midFile='extraFullTopLevel.tsv'
		outFile='aidaTopLevel.tsv'
		pickleFile='topics/topicsTop.p'
	else:
		topics=['INTERNATIONAL_RELATIONS WAR_CIVIL_WAR', 'REGULATION/POLICY INSOLVENCY/LIQUIDITY', 'DOMESTIC_POLITICS', 'STRATEGY/PLANS REGULATION/POLICY PRODUCTION/SERVICES', 'RELIGION WAR_CIVIL_WAR', 'HUMAN_INTEREST', 'MERGERS/ACQUISITIONS', 'CRIME_LAW_ENFORCEMENT DOMESTIC_POLITICS', 'COMMENT/FORECASTS MARKET_SHARE', 'DOMESTIC_POLITICS BIOGRAPHIES_PERSONALITIES_PEOPLE', 'STRATEGY/PLANS REGULATION/POLICY MONOPOLIES/COMPETITION', 'ECONOMIC_PERFORMANCE', 'BOND_MARKETS', 'INTERBANK_MARKETS', 'DOMESTIC_POLITICS WAR_CIVIL_WAR', 'PRODUCTION/SERVICES SOFT_COMMODITIES', 'PRODUCTION/SERVICES ENERGY_MARKETS', 'MERCHANDISE_TRADE LABOUR_ISSUES', 'EC_MONETARY/ECONOMIC DOMESTIC_POLITICS', 'STRATEGY/PLANS INTERNATIONAL_RELATIONS', 'CRIME_LAW_ENFORCEMENT INTERNATIONAL_RELATIONS WAR_CIVIL_WAR', 'DOMESTIC_MARKETS MERCHANDISE_TRADE EC_EXTERNAL_RELATIONS', 'INTERNATIONAL_RELATIONS DOMESTIC_POLITICS', 'SPORTS', 'CAPACITY/FACILITIES WEATHER', 'FOREX_MARKETS', 'EXPENDITURE/REVENUE DOMESTIC_POLITICS', 'DISASTERS_AND_ACCIDENTS', 'GOVERNMENT_BORROWING', 'SOFT_COMMODITIES', 'INTERNATIONAL_RELATIONS', 'REGULATION/POLICY CAPACITY/FACILITIES MERCHANDISE_TRADE', 'NONE', 'REGULATION/POLICY INTERNATIONAL_RELATIONS SCIENCE_AND_TECHNOLOGY', 'CRIME_LAW_ENFORCEMENT HUMAN_INTEREST', 'MANAGEMENT_MOVES', 'ENERGY_MARKETS', 'STRATEGY/PLANS CAPACITY/FACILITIES', 'CAPACITY/FACILITIES TRAVEL_AND_TOURISM', 'WAR_CIVIL_WAR', 'DOMESTIC_POLITICS SPORTS', 'CAPACITY/FACILITIES', 'DOMESTIC_POLITICS ELECTIONS', 'REGULATION/POLICY EC_AGRICULTURE_POLICY', 'REGULATION/POLICY INTERNATIONAL_RELATIONS', 'INTERNATIONAL_RELATIONS RELIGION', 'SHARE_CAPITAL', 'CRIME_LAW_ENFORCEMENT', 'EQUITY_MARKETS', 'INTERNATIONAL_RELATIONS DOMESTIC_POLITICS WAR_CIVIL_WAR', 'HEALTH', 'DEFENCE INTERNATIONAL_RELATIONS', 'MERCHANDISE_TRADE', 'HEALTH HUMAN_INTEREST', 'COMMENT/FORECASTS', 'CRIME_LAW_ENFORCEMENT WAR_CIVIL_WAR', 'ADVERTISING/PROMOTION', 'DISASTERS_AND_ACCIDENTS WEATHER', 'DOMESTIC_MARKETS', 'NEW_PRODUCTS/SERVICES']
		inFile='CONLL/AIDA-YAGO2-dataset_topicsLowlevel.tsv'
		midFile='extraFullLowLevel.tsv'
		outFile='aidaLowLevel.tsv'
		pickleFile='topics/topicsLow.p'
		if sys.argv[1]!='low':
			aggregateTopics=False
			outFile='aidaSingleArticles.tsv'
			#midFile='extraFullSingle.tsv'
	#topics=['DOMESTIC_POLITICS']
	total=1
	start = time.time()
	factorWeights={'wc':0.525,'wss': 0.325, 'wa': 0.05, 'wr':0.05, 'wt': 0.05}

	import pickle
	timePickle=pickle.load(open('200712_agg.p', 'rb'))
	print("Pickle loaded")

	if sys.argv[2]=='my' and os.path.exists(outFile):
		os.remove(outFile)
		os.remove('noreread.' + outFile)
	elif sys.argv[2]!='my' and os.path.exists(midFile):
		os.remove(midFile)
	#topics=['WAR_CIVIL_WAR']
	for topic in topics:
		runs=1
		while runs<=total:
			print("Topic: %s. Starting run %d/%d" % (topic, runs, total))
			if sys.argv[2]=='my':
				my_system.run(midFile, outFile, pickleFile, topic, factorWeights, aggregateTopics, timePickle)
			else:
				run_agdistis.run(inFile, midFile, topic, aggregateTopics)
			runs+=1
	if sys.argv[2]=='my': # MY SYSTEM
		p, r, f=utils.computeStats(outFile, False)
	else: # AGDISTIS
		p, r, f=utils.computeStats(midFile, True)
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
	end = time.time()
	print("Took %s seconds." % str(end - start))
