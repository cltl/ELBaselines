import re
import sys

if __name__=='__main__':
	topic='WAR_CIVIL_WAR'
	fn=sys.argv[1]
	articles=['1314testb Third', '1212testb GUNMEN', '1313testb Italy', '1304testb Turkey', '1305testb Three', '1332testb Burmese', '1317testb Moslem', '1266testb Government', '1267testb Burmese']
	file = open(fn, "r")
	for line in file:
		line=line.strip()
		for article in sorted(articles):
			if re.search(article, line):
				lineArray=line.split('\t')
				mention=lineArray[6]
				print(mention)
