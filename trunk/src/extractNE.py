import re
import sys

def getGroup(item):
	if(item):
		return item.group(1).lower()

def getNamedEntities(path):
	lines = map(lambda line: line, open(path).xreadlines())
	locations = list(set(filter(lambda x: x != None, map(lambda line: getGroup(re.search('<ENAMEX TYPE="LOCATION">([^<>]*)</ENAMEX>',line)),lines))))
	persons = list(set(filter(lambda x: x != None, map(lambda line: getGroup(re.search('<ENAMEX TYPE="PERSON">([^<>]*)</ENAMEX>',line)),lines))))
	times = list(set(filter(lambda x: x != None, map(lambda line: getGroup(re.search('<TIMEX TYPE="DATE">([^<>]*)</TIMEX>',line)),lines))))
	return locations, persons, times

print getNamedEntities(sys.argv[1])