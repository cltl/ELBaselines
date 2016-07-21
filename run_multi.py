import sys
import my_system
import time
import os
import utils

if __name__=='__main__':
	topics=['INTERNATIONAL_RELATIONS WAR_CIVIL_WAR', 'REGULATION/POLICY INSOLVENCY/LIQUIDITY', 'DOMESTIC_POLITICS', 'STRATEGY/PLANS REGULATION/POLICY PRODUCTION/SERVICES', 'RELIGION WAR_CIVIL_WAR', 'HUMAN_INTEREST', 'MERGERS/ACQUISITIONS', 'CRIME_LAW_ENFORCEMENT DOMESTIC_POLITICS', 'COMMENT/FORECASTS MARKET_SHARE', 'DOMESTIC_POLITICS BIOGRAPHIES_PERSONALITIES_PEOPLE', 'STRATEGY/PLANS REGULATION/POLICY MONOPOLIES/COMPETITION', 'ECONOMIC_PERFORMANCE', 'BOND_MARKETS', 'INTERBANK_MARKETS', 'DOMESTIC_POLITICS WAR_CIVIL_WAR', 'PRODUCTION/SERVICES SOFT_COMMODITIES', 'PRODUCTION/SERVICES ENERGY_MARKETS', 'MERCHANDISE_TRADE LABOUR_ISSUES', 'EC_MONETARY/ECONOMIC DOMESTIC_POLITICS', 'STRATEGY/PLANS INTERNATIONAL_RELATIONS', 'CRIME_LAW_ENFORCEMENT INTERNATIONAL_RELATIONS WAR_CIVIL_WAR', 'DOMESTIC_MARKETS MERCHANDISE_TRADE EC_EXTERNAL_RELATIONS', 'INTERNATIONAL_RELATIONS DOMESTIC_POLITICS', 'SPORTS', 'CAPACITY/FACILITIES WEATHER', 'FOREX_MARKETS', 'EXPENDITURE/REVENUE DOMESTIC_POLITICS', 'DISASTERS_AND_ACCIDENTS', 'GOVERNMENT_BORROWING', 'SOFT_COMMODITIES', 'INTERNATIONAL_RELATIONS', 'REGULATION/POLICY CAPACITY/FACILITIES MERCHANDISE_TRADE', 'NONE', 'REGULATION/POLICY INTERNATIONAL_RELATIONS SCIENCE_AND_TECHNOLOGY', 'CRIME_LAW_ENFORCEMENT HUMAN_INTEREST', 'MANAGEMENT_MOVES', 'ENERGY_MARKETS', 'STRATEGY/PLANS CAPACITY/FACILITIES', 'CAPACITY/FACILITIES TRAVEL_AND_TOURISM', 'WAR_CIVIL_WAR', 'DOMESTIC_POLITICS SPORTS', 'CAPACITY/FACILITIES', 'DOMESTIC_POLITICS ELECTIONS', 'REGULATION/POLICY EC_AGRICULTURE_POLICY', 'REGULATION/POLICY INTERNATIONAL_RELATIONS', 'INTERNATIONAL_RELATIONS RELIGION', 'SHARE_CAPITAL', 'CRIME_LAW_ENFORCEMENT', 'EQUITY_MARKETS', 'INTERNATIONAL_RELATIONS DOMESTIC_POLITICS WAR_CIVIL_WAR', 'HEALTH', 'DEFENCE INTERNATIONAL_RELATIONS', 'MERCHANDISE_TRADE', 'HEALTH HUMAN_INTEREST', 'COMMENT/FORECASTS', 'CRIME_LAW_ENFORCEMENT WAR_CIVIL_WAR', 'ADVERTISING/PROMOTION', 'DISASTERS_AND_ACCIDENTS WEATHER', 'DOMESTIC_MARKETS', 'NEW_PRODUCTS/SERVICES']
	#topics=['WAR_CIVIL_WAR', 'INTERNATIONAL_RELATIONS DOMESTIC_POLITICS']
	total=1
	start = time.time()
	factorWeights={'wc':0.5,'wss': 0.4, 'wa': 0.05, 'wr':0.05}
	os.remove('aidaMyOutput.tsv')
	for topic in topics:
		score=0.0
		runs=1
		while runs<=total:
			print("Topic: %s. Starting run %d/%d" % (topic, runs, total))
			my_system.run(sys.argv[1], topic, factorWeights)
			runs+=1
		#print("Average f-score is %f" % (score/total))

	p, r, f=utils.computeStats("aidaMyOutput.tsv", False)
	print("Precision: %f, Recall: %f, F1-value: %f" % (p, r, f))
	end = time.time()
	print("Took %s seconds." % str(end - start))
